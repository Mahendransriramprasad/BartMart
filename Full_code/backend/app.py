from flask import Flask, request, jsonify, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_cors import CORS
from bson.errors import InvalidId
from bson import ObjectId, errors  # Import errors.InvalidId
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/ecommerce"
app.secret_key = "Suba@123"
CORS(app, supports_credentials=True)  # Enable CORS for React frontend

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Dummy Admin Credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Helper Functions
def calculate_age(dob):
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@app.route("/product/<product_id>", methods=["GET"])
def get_product(product_id):
    try:
        print("Received Product ID:", product_id)  # Debugging

        # Check if ID is an ObjectId or a string
        if not ObjectId.is_valid(product_id):
            print("Invalid ObjectId format")
            return jsonify({"error": "Invalid Product ID format"}), 400

        try:
            product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        except errors.InvalidId:  # Catching invalid ObjectId conversion error
            print("Error: Invalid ObjectId conversion")
            return jsonify({"error": "Invalid Product ID format"}), 400

        if not product:
            print("Product not found in DB")
            return jsonify({"error": "Product not found"}), 404

        product["_id"] = str(product["_id"])  # Convert ObjectId to string
        return jsonify(product), 200

    except Exception as e:
        print("Error:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500

# Home Route - Fetch All Products
@app.route("/", methods=["GET"])
def home():
    products = list(mongo.db.products.find())
    # Convert ObjectId to string for each product
    for product in products:
        product["_id"] = str(product["_id"])
    if "username" not in session:
        return jsonify({"all_products": products})

    user = mongo.db.users.find_one({"username": session["username"]})
    if not user:
        session.clear()
        return jsonify({"error": "User session not found"})

    age = calculate_age(user["dob"]) if "dob" in user else None
    age_group = "Kids" if age and age < 13 else "Teens" if 13 <= age <= 19 else "Adults"

    suggested_products = list(mongo.db.products.find({"age_group": age_group})) if age_group else []

    return jsonify({
        "suggested_products": suggested_products,
        "all_products": products,
        "user": user
    })

# User Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data["username"]
    password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')
    dob = data["dob"]

    existing_user = mongo.db.users.find_one({"username": username})
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    mongo.db.users.insert_one({
        "username": username,
        "password": password,
        "dob": dob,
        "coins": 100,
        "cart": {},
        "sold_products": [],
        "avatar": None,
        "bio": ""
    })
    return jsonify({"message": "Registration successful!"}), 201

# User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    # Check for admin login
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["admin"] = True
        return jsonify({"message": "Admin login successful!", "username": username}), 200

    # Check for regular user login
    user = mongo.db.users.find_one({"username": username})
    if user and bcrypt.check_password_hash(user["password"], password):
        session["username"] = username
        return jsonify({"message": "Login successful!", "username": username}), 200

    return jsonify({"error": "Invalid credentials"}), 400

@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = mongo.db.users.find_one({"username": session["username"]})
    if not user:
        return jsonify({"error": "User not found"}), 404

    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404

    cart = mongo.db.carts.find_one({"username": session["username"]})
    if not cart:
        cart = {"username": session["username"], "items": []}
        mongo.db.carts.insert_one(cart)

    mongo.db.carts.update_one(
        {"username": session["username"]},
        {"$push": {"items": {"_id": product_id, "quantity": 1}}}
    )

    return jsonify({"message": "Product added to cart"}), 200

# View Cart
@app.route("/cart", methods=["GET"])
def cart():
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = mongo.db.users.find_one({"username": session["username"]})
    cart = mongo.db.carts.find_one({"username": session["username"]})

    if not cart or "items" not in cart or len(cart["items"]) == 0:
        return jsonify({"cart_items": [], "total_cost": 0})

    cart_items = []
    total_cost = 0

    for item in cart["items"]:
        product = mongo.db.products.find_one({"_id": ObjectId(item["_id"])})
        if product:
            product["quantity"] = item["quantity"]
            cart_items.append(product)
            total_cost += product["price"] * item["quantity"]

    return jsonify({"cart_items": cart_items, "total_cost": total_cost})
# Checkout
@app.route("/checkout", methods=["POST"])
def checkout():
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = mongo.db.users.find_one({"username": session["username"]})
    cart = mongo.db.carts.find_one({"username": session["username"]})

    if not cart or "items" not in cart or len(cart["items"]) == 0:
        return jsonify({"error": "Cart is empty"}), 400

    total_cost = sum(item["quantity"] * mongo.db.products.find_one({"_id": ObjectId(item["_id"])})["price"] for item in cart["items"])

    if user["coins"] < total_cost:
        return jsonify({"error": "Not enough coins to complete the purchase"}), 400

    mongo.db.users.update_one({"username": session["username"]}, {"$inc": {"coins": -total_cost}})
    mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": []}})

    return jsonify({"message": "Checkout successful"}), 200
# Admin Dashboard - Fetch All Products and Pending Requests
@app.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    if "admin" not in session:
        return jsonify({"error": "Admin not logged in"}), 401

    products = list(mongo.db.products.find())
    sell_requests = list(mongo.db.sell_requests.find({"status": "Pending"}))
    return jsonify({"products": products, "sell_requests": sell_requests})
# Admin Approve Product
@app.route("/admin/approve_product/<request_id>", methods=["POST"])
def approve_product(request_id):
    if "admin" not in session:
        return jsonify({"error": "Admin not logged in"}), 401

    product = mongo.db.sell_requests.find_one({"_id": ObjectId(request_id)})
    if product:
        product["status"] = "Approved"
        mongo.db.products.insert_one(product)
        mongo.db.sell_requests.delete_one({"_id": ObjectId(request_id)})
        mongo.db.users.update_one({"username": product["username"]}, {"$inc": {"coins": 100}})
        return jsonify({"message": "Product approved and added to store!"}), 200

    return jsonify({"error": "Product not found"}), 404

# Admin Reject Product
@app.route("/admin/reject_product/<request_id>", methods=["POST"])
def reject_product(request_id):
    if "admin" not in session:
        return jsonify({"error": "Admin not logged in"}), 401

    mongo.db.sell_requests.update_one({"_id": ObjectId(request_id)}, {"$set": {"status": "Rejected"}})
    return jsonify({"message": "Product rejected!"}), 200

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    session.pop("admin", None)
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)