from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/ecommerce"
app.secret_key = "Suba@123"

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Enable CORS for all routes
CORS(app)

# Dummy Admin Credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def calculate_age(dob):
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Home Page (Products Display)
@app.route("/", methods=["GET"])
def home():
    products = list(mongo.db.products.find())
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
    if request.is_json:
        data = request.get_json()
        username = data["username"]
        password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')
        dob = data["dob"]
    else:
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        dob = request.form["dob"]

    existing_user = mongo.db.users.find_one({"username": username})
    if existing_user:
        flash("Username already exists.", "error")
        return jsonify({"error": "Username already exists"}), 400

    mongo.db.users.insert_one({"username": username, "password": password, "dob": dob, "coins": 100, "cart": {}})
    flash("Registration successful!", "success")
    return jsonify({"message": "Registration successful!"})

# User & Admin Login
@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        data = request.get_json()  # Ensure this is properly handled
        try:
            username = data["username"]
            password = data["password"]
        except KeyError as e:
            return jsonify({"error": f"Missing field: {str(e)}"}), 400
    else:
        return jsonify({"error": "Expected JSON format"}), 400

    # Simulate user lookup (you can replace this with real logic)
    user = mongo.db.users.find_one({"username": username})
    if user and bcrypt.check_password_hash(user["password"], password):
        session["username"] = username  # Store user session if login is successful
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 400

@app.route("/sell", methods=["GET", "POST"])
def sell():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})

    if request.method == "POST":
        product_data = {
            "username": session["username"],
            "name": request.form["name"],
            "category": request.form["category"],
            "image": request.form["image"],
            "price": int(request.form["price"]),
            "age_group": request.form["age_group"],
            "status": "Pending"
        }
        mongo.db.sell_requests.insert_one(product_data)
        flash("Product submitted for review!", "success")
        return redirect(url_for("home"))

    return render_template("sell.html", user=user)

@app.route("/admin/review_products")
def review_products():
    if "admin" not in session:
        return redirect(url_for("login"))

    pending_products = list(mongo.db.sell_requests.find({"status": "Pending"}))
    return render_template("review_products.html", pending_products=pending_products)

@app.route("/admin/approve_product/<request_id>")
def approve_product(request_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    product = mongo.db.sell_requests.find_one({"_id": ObjectId(request_id)})
    if product:
        product["status"] = "Approved"
        mongo.db.products.insert_one(product)
        mongo.db.sell_requests.delete_one({"_id": ObjectId(request_id)})
        mongo.db.users.update_one({"username": product["username"]}, {"$inc": {"coins": 100}})
        flash("Product approved and added to store!", "success")
    return redirect(url_for("review_products"))

@app.route("/admin/reject_product/<request_id>")
def reject_product(request_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    mongo.db.sell_requests.update_one({"_id": ObjectId(request_id)}, {"$set": {"status": "Rejected"}})
    flash("Product rejected!", "error")
    return redirect(url_for("review_products"))

@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        product_data = {
            "category": request.form["category"],
            "name": request.form["name"],
            "image": request.form["image"],
            "price": int(request.form["price"]),
            "age_group": request.form["age_group"]
        }
        mongo.db.products.insert_one(product_data)
        flash("Product added successfully!", "success")

    products = list(mongo.db.products.find())
    sell_requests = list(mongo.db.sell_requests.find({"status": "Pending"}))
    return render_template("admin_dashboard.html", products=products, sell_requests=sell_requests)

@app.route("/admin/delete_product/<product_id>")
def delete_product(product_id):
    if "admin" not in session:
        return redirect(url_for("login"))
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    flash("Product deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))

# Add to Cart
@app.route("/add_to_cart/<product_id>", methods=["GET"])
def add_to_cart(product_id):
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = mongo.db.users.find_one({"username": session["username"]})
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})

    if not product:
        return jsonify({"error": "Product not found"}), 404

    cart = mongo.db.carts.find_one({"username": user["username"]})

    if cart:
        for item in cart["items"]:
            if item["_id"] == str(product_id):
                item["quantity"] += 1
                break
        else:
            cart["items"].append({"_id": str(product_id), "quantity": 1})

        mongo.db.carts.update_one({"username": user["username"]}, {"$set": {"items": cart["items"]}})
    else:
        mongo.db.carts.insert_one({"username": user["username"], "items": [{"_id": str(product_id), "quantity": 1}]})

    return jsonify({"message": "Product added to cart successfully"})

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

@app.route("/update_cart_quantity/<product_id>/<action>", methods=["GET"])
def update_cart_quantity(product_id, action):
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    cart = mongo.db.carts.find_one({"username": session["username"]})

    if not cart or "items" not in cart:
        return jsonify({"error": "No items in cart"}), 404

    for item in cart["items"]:
        if item["_id"] == product_id:
            if action == "increase":
                item["quantity"] += 1
            elif action == "decrease" and item["quantity"] > 1:
                item["quantity"] -= 1
            break

    # Update the cart in the database
    mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": cart["items"]}})

    return jsonify({"message": "Cart updated successfully"})

@app.route("/checkout", methods=["POST"])
def checkout():
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = mongo.db.users.find_one({"username": session["username"]})
    cart = mongo.db.carts.find_one({"username": session["username"]})

    if not cart or "items" not in cart or len(cart["items"]) == 0:
        return jsonify({"error": "Cart is empty"}), 400

    # Calculate total cost
    total_cost = sum(item["quantity"] * mongo.db.products.find_one({"_id": ObjectId(item["_id"])})["price"] for item in cart["items"])

    # Check if user has enough coins
    if user["coins"] < total_cost:
        return jsonify({"error": "Not enough coins to complete the purchase"}), 400

    # Deduct coins
    mongo.db.users.update_one({"username": session["username"]}, {"$inc": {"coins": -total_cost}})

    # Clear the cart after checkout
    mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": []}})

    return jsonify({"message": "Checkout successful"})

@app.route("/checkout_success", methods=["GET"])
def checkout_success():
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = mongo.db.users.find_one({"username": session["username"]})

    return jsonify({"message": "Checkout complete", "user": user})

@app.route("/remove_from_cart/<product_id>", methods=["GET"])
def remove_from_cart(product_id):
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    cart = mongo.db.carts.find_one({"username": session["username"]})

    if cart:
        cart["items"] = [item for item in cart["items"] if str(item["_id"]) != product_id]
        mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": cart["items"]}})

    return jsonify({"message": "Item removed from cart successfully"})

# Logout
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    session.pop("admin", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
