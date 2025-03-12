from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/ecommerce"
app.secret_key = "suba@123"
app.config['SESSION_COOKIE_SECURE'] = False

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

products_collection = mongo.db.products  # Access collection directly through PyMongo's db object
negotiate_collection = mongo.db.negotiations  # Access collection directly through PyMongo's db object
# Dummy Admin Credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_product_by_id(product_id):
    return products_collection.find_one({"_id": product_id})

def get_seller_by_id(product_id):
    return negotiate_collection.find_one({"_id": product_id})
def calculate_age(dob):
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Home Page (Products Display)
@app.route("/")
def home():
    print(f"Session: {session}")  # Debugging output to check session
    products = list(mongo.db.products.find())

    # If user is NOT logged in, show all products
    if "username" not in session:
        return render_template("index.html", all_products=products, user=None)

    user = mongo.db.users.find_one({"username": session["username"]})
    if not user:
        session.clear()
        return redirect(url_for("home"))

    age = calculate_age(user["dob"]) if "dob" in user else None
    age_group = "Kids" if age and age < 13 else "Teens" if 13 <= age <= 19 else "Adults"

    suggested_products = list(mongo.db.products.find({"age_group": age_group})) if age_group else []

    return render_template(
        "index.html",
        suggested_products=suggested_products,
        all_products=products,
        user=user
    )

# User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        dob = request.form["dob"]

        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        mongo.db.users.insert_one({"username": username, "password": password, "dob": dob, "coins": 100, "cart": {}, "sold_products": []})
        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# User & Admin Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check for admin login
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        # Check for regular user login
        user = mongo.db.users.find_one({"username": username})
        if user and bcrypt.check_password_hash(user["password"], password):
            session["username"] = username  # Set the session username here
            flash("Login successful!", "success")
            return redirect(url_for("home"))

        flash("Invalid credentials. Try again.", "error")

    return render_template("login.html")

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
            "description": request.form["description"],  # New field for description
            "image1": request.form["image1"] if "image1" in request.form else None,
            "image2": request.form["image2"] if "image2" in request.form else None,
            "image3": request.form["image3"] if "image3" in request.form else None,
            "image4": request.form["image4"] if "image4" in request.form else None,
            "price": int(request.form["price"]),
            "age_group": request.form["age_group"],
            "status": "Pending"
        }

        # Insert the product into the 'sell_requests' collection
        product_id = mongo.db.sell_requests.insert_one(product_data).inserted_id
        
        # Update the user's profile with the new product ID in the 'sold_products' list
        mongo.db.users.update_one(
            {"username": session["username"]},
            {"$push": {"sold_products": str(product_id)}}  # Store product ID in 'sold_products' field
        )

        flash("Product submitted for review!", "success")
        return redirect(url_for("home"))

    return render_template("sell.html", user=user)

@app.route("/my_products")
def my_products():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})

    # Fetch all product IDs from sold_products in the user's profile (successful sales)
    sold_product_ids = user.get("sold_products", [])

    # Fetch products that are still pending approval
    pending_products = list(mongo.db.sell_requests.find({"username": session["username"], "status": "Pending"}))

    # Fetch products that have been approved and are in the store (successful sales)
    sold_products = []
    for product_id in sold_product_ids:
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        if product:
            sold_products.append(product)

    return render_template(
        "my_products.html",
        user=user,
        pending_products=pending_products,  # Products that are still pending
        sold_products=sold_products  # Products that are successfully sold
    )
# Example in the route to view product details:
@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        product = get_product_by_id(ObjectId(product_id))  # Ensure it's an ObjectId
        # Fetch the seller's details using the product's "username"
        seller = mongo.db.users.find_one({"username": product["username"]})
        seller_name = seller["username"] if seller else "Unknown"

        # Fetch the negotiation details if available
        negotiate = get_seller_by_id(ObjectId(product_id))  # Ensure it's an ObjectId

        # Fetch the current logged-in user (if any)
        user = None
        if "username" in session:
            user = mongo.db.users.find_one({"username": session["username"]})

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("home"))
    
    return render_template(
        'product_detail.html',
        product=product,
        negotiate_price=negotiate,
        seller_name=seller_name,
        user=user  # Pass the user to the template
    )
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

# Delete Product (Admin)
@app.route("/admin/delete_product/<product_id>")
def delete_product(product_id):
    if "admin" not in session:
        return redirect(url_for("login"))
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    flash("Product deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))

# Add to Cart
@app.route("/add_to_cart/<product_id>")
def add_to_cart(product_id):
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})

    if not product:
        return "Product not found!", 404

    cart = mongo.db.carts.find_one({"username": user["username"]})

    if cart:
        for item in cart["items"]:
            if item["_id"] == str(product_id):  # Check if product is already in the cart
                item["quantity"] += 1
                break
        else:
            cart["items"].append({"_id": str(product_id), "quantity": 1})

        mongo.db.carts.update_one({"username": user["username"]}, {"$set": {"items": cart["items"]}})
    else:
        mongo.db.carts.insert_one({"username": user["username"], "items": [{"_id": str(product_id), "quantity": 1}]})

    return redirect(url_for("cart"))

# View Cart
@app.route("/cart")
def cart():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    cart = mongo.db.carts.find_one({"username": session["username"]})

    if not cart or "items" not in cart or len(cart["items"]) == 0:
        return render_template("cart.html", cart_items=[], total_cost=0, user=user)

    cart_items = []
    total_cost = 0

    for item in cart["items"]:
        product = mongo.db.products.find_one({"_id": ObjectId(item["_id"])})
        if product:
            product["quantity"] = item["quantity"]
            cart_items.append(product)
            total_cost += product["price"] * item["quantity"]  # Update total cost

    return render_template("cart.html", cart_items=cart_items, total_cost=total_cost, user=user)

@app.route("/update_cart_quantity/<product_id>/<action>")
def update_cart_quantity(product_id, action):
    if "username" not in session:
        return redirect(url_for("login"))

    cart = mongo.db.carts.find_one({"username": session["username"]})

    if not cart or "items" not in cart:
        return redirect(url_for("cart"))

    for item in cart["items"]:
        if item["_id"] == product_id:
            if action == "increase":
                item["quantity"] += 1
            elif action == "decrease" and item["quantity"] > 1:
                item["quantity"] -= 1
            break

    # Update the cart in the database
    mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": cart["items"]}})

    return redirect(url_for("cart"))

@app.route("/checkout", methods=["POST"])
def checkout():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    cart = mongo.db.carts.find_one({"username": session["username"]})

    if not cart or "items" not in cart or len(cart["items"]) == 0:
        return redirect(url_for("cart"))

    # Calculate total cost
    total_cost = sum(item["quantity"] * mongo.db.products.find_one({"_id": ObjectId(item["_id"])})["price"] for item in cart["items"])

    # Check if user has enough coins
    if user["coins"] < total_cost:
        return "⚠️ Not enough coins to complete the purchase. Earn more coins and try again."

    # Deduct coins
    mongo.db.users.update_one({"username": session["username"]}, {"$inc": {"coins": -total_cost}})

    # Clear the cart after checkout
    mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": []}})

    return redirect(url_for("checkout_success"))  # Redirect to checkout success page

@app.route("/checkout_success")
def checkout_success():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})

    # Display checkout success message
    return render_template("checkout_success.html", user=user)

@app.route("/remove_from_cart/<product_id>")
def remove_from_cart(product_id):
    if "username" not in session:
        return redirect(url_for("login"))

    cart = mongo.db.carts.find_one({"username": session["username"]})

    if cart:
        cart["items"] = [item for item in cart["items"] if str(item["_id"]) != product_id]
        mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": cart["items"]}})

    return redirect(url_for("cart"))
@app.route("/negotiate/<product_id>", methods=["GET", "POST"])
def negotiate_price(product_id):
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})

    if not product:
        return "Product not found!", 404

    if request.method == "POST":
        proposed_price = int(request.form["proposed_price"])

        # Insert the negotiation request into the 'negotiations' collection
        negotiation_data = {
            "buyer": user["username"],
            "product_id": product_id,
            "product_name": product["name"],
            "proposed_price": proposed_price,
            "status": "Pending",  # Negotiation is pending until seller approves or rejects
            "seller": product["username"],  # Seller is the user who posted the product
        }

        mongo.db.negotiations.insert_one(negotiation_data)
        flash("Negotiation request sent to seller!", "success")
        return redirect(url_for("home"))

    return render_template("negotiate.html", product=product, user=user)

@app.route("/my_negotiations")
def my_negotiations():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    
    # Find all negotiations where the user is the seller
    negotiations = list(mongo.db.negotiations.find({"seller": user["username"], "status": "Pending"}))

    return render_template("my_products.html", negotiations=negotiations, user=user)

@app.route("/approve_negotiation/<negotiation_id>")
def approve_negotiation(negotiation_id):
    if "username" not in session:
        return redirect(url_for("login"))

    negotiation = mongo.db.negotiations.find_one({"_id": ObjectId(negotiation_id)})

    if negotiation:
        # Update negotiation status to 'Approved'
        mongo.db.negotiations.update_one(
            {"_id": ObjectId(negotiation_id)},
            {"$set": {"status": "Approved"}}
        )

        # Update the price of the product to the proposed price
        product = mongo.db.products.find_one({"_id": ObjectId(negotiation["product_id"])})

        if product:
            mongo.db.products.update_one(
                {"_id": ObjectId(negotiation["product_id"])},
                {"$set": {"price": negotiation["proposed_price"]}}
            )

        # Notify the buyer (the user who initiated the negotiation)
        buyer = mongo.db.users.find_one({"username": negotiation["buyer"]})
        if buyer:
            flash(f"Negotiation for {product['name']} approved! Price is now {negotiation['proposed_price']} coins.", "success")
            # Optionally, you can add a message to inform the buyer about the approval
            mongo.db.messages.insert_one({
                "receiver": buyer["username"],
                "sender": "Admin",
                "message": f"Your negotiation for {product['name']} has been approved. The price is now {negotiation['proposed_price']} coins.",
                "date": datetime.now()
            })

        flash("Negotiation approved! Price updated.", "success")
    else:
        flash("Negotiation not found.", "error")
    
    return redirect(url_for("my_negotiations"))
    
@app.route("/reject_negotiation/<negotiation_id>")
def reject_negotiation(negotiation_id):
    if "username" not in session:
        return redirect(url_for("login"))

    negotiation = mongo.db.negotiations.find_one({"_id": ObjectId(negotiation_id)})
    
    if negotiation:
        # Update negotiation status to 'Rejected'
        mongo.db.negotiations.update_one(
            {"_id": ObjectId(negotiation_id)},
            {"$set": {"status": "Rejected"}}
        )
        flash("Negotiation rejected.", "error")
    else:
        flash("Negotiation not found.", "error")
    
    return redirect(url_for("my_negotiations"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("admin", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
