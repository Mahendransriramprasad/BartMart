from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

import os
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/ecommerce";
app.secret_key = "bartMart"
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
    if not dob:
        return None
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
# Home Page (Products Display)
@app.route("/")
def home():
    print(f"Session: {session}")  # Debugging output to check session

    # Fetch all products (excluding those sold by the logged-in user)
    if "username" in session:
        user = mongo.db.users.find_one({"username": session["username"]})
        if not user:
            session.clear()
            return redirect(url_for("home"))

        # Exclude products sold by the logged-in user
        all_products = list(mongo.db.products.find({"username": {"$ne": user["username"]}}))
    else:
        # If user is not logged in, show all products
        all_products = list(mongo.db.products.find())
        user = None

    # If user is logged in, calculate age group and fetch suggested/recommended products
    if user:
        # Calculate age and age group
        age = calculate_age(user["dob"]) if "dob" in user else None
        age_group = "Kids" if age and age < 13 else "Teens" if 13 <= age <= 19 else "Adults"

        # Fetch suggested products based on age group
        suggested_products = list(mongo.db.products.find({"age_group": age_group, "username": {"$ne": user["username"]}})) if age_group else []

        # Fetch recommended products based on purchase history
        purchase_history = user.get("purchase_history", [])
        if purchase_history:
            purchased_categories = set(purchase["category"] for purchase in purchase_history if "category" in purchase)
            recommended_products = list(mongo.db.products.find({
                "category": {"$in": list(purchased_categories)},
                "username": {"$ne": user["username"]}  # Exclude products sold by the same user
            }))
        else:
            recommended_products = []
    else:
        # If user is not logged in, show no suggested or recommended products
        suggested_products = []
        recommended_products = []

    return render_template(
        "index.html",
        suggested_products=suggested_products,
        recommended_products=recommended_products,
        all_products=all_products,
        user=user
    )
@app.route("/search")
def search_products():
    # Get query parameters
    query = request.args.get("query", "").strip()  # Search term from the search bar
    category = request.args.get("category", "").strip()  # Category filter
    min_price = request.args.get("min_price", type=float)  # Minimum price filter
    max_price = request.args.get("max_price", type=float)  # Maximum price filter

    # Initialize search query
    search_query = {}

    # Exclude products of the logged-in user
    if "username" in session:
        user = mongo.db.users.find_one({"username": session["username"]})
        if user:
            search_query["username"] = {"$ne": user["username"]}  # Exclude logged-in user's products

    # Apply search filters
    if query:
        search_query["name"] = {"$regex": query, "$options": "i"}  # Case-insensitive search by name
    if category:
        search_query["category"] = category  # Filter by category
    if min_price is not None or max_price is not None:
        search_query["price"] = {}
        if min_price is not None:
            search_query["price"]["$gte"] = min_price  # Products with price >= min_price
        if max_price is not None:
            search_query["price"]["$lte"] = max_price  # Products with price <= max_price

    # Fetch products matching the search query
    products = list(mongo.db.products.find(search_query))

    return render_template(
        "search_results.html",
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        products=products,
        user=session.get("username")
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    if not user:
        flash("User not found!", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        bio = request.form.get("bio")
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        avatar = request.files.get("avatar")

        # Address fields
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")
        pincode = request.form.get("pincode")
        country = request.form.get("country")

        # Calculate age
        age = calculate_age(dob) if dob else None

        update_data = {
            "bio": bio,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
            "gender": gender,
            "age": age,  # ✅ Store age
            "address": {
                "street": street,
                "city": city,
                "state": state,
                "pincode": pincode,
                "country": country,
            },  # ✅ Store address
        }

        if avatar:
            allowed_extensions = {"png", "jpg", "jpeg", "gif"}
            if "." in avatar.filename and avatar.filename.rsplit(".", 1)[-1].lower() in allowed_extensions:
                avatars_dir = os.path.join("static", "avatars")
                os.makedirs(avatars_dir, exist_ok=True)

                avatar_filename = f"{username}_{avatar.filename}"
                avatar_path = os.path.join(avatars_dir, avatar_filename)
                avatar.save(avatar_path)
                update_data["avatar"] = avatar_filename
            else:
                flash("Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.", "error")

        mongo.db.users.update_one({"username": session["username"]}, {"$set": update_data})
        flash("Profile updated successfully!", "success")

        # Update session if username is changed
        session["username"] = username

        return redirect(url_for("profile"))

    # Pass age and address to template
    age = calculate_age(user.get("dob"))
    address = user.get("address", {})

    return render_template("profile.html", user=user, age=age, address=address)

@app.route("/profile/<username>")
def profile_view(username):
    # Fetch the seller's details from the database
    seller = mongo.db.users.find_one({"username": username})
    if not seller:
        flash("Seller not found.", "error")
        return redirect(url_for("home"))

    # Fetch the seller's sold products
    sold_products = []
    if seller.get("sold_products"):
        sold_products = list(
            mongo.db.products.find(
                {"_id": {"$in": [ObjectId(product_id) for product_id in seller["sold_products"]]}}
            )
        )

    # Fetch the current logged-in user (optional)
    user = None
    if "username" in session:
        user = mongo.db.users.find_one({"username": session["username"]})

    return render_template("profileview.html", seller=seller, sold_products=sold_products, user=user)

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

        mongo.db.users.insert_one({
            "username": username,
            "password": password,
            "dob": dob,
            "coins": 100,
            "cart": {},
            "sold_products": [],
            "avatar": None,  # Initialize avatar as None
            "bio": ""  # Initialize bio as an empty string
        })
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

        # Check if username exists
        user = mongo.db.users.find_one({"username": username})
        if user:
            # Check if password matches
            if bcrypt.check_password_hash(user["password"], password):
                session["username"] = username
                return redirect(url_for("home"))  # No success flash needed
            else:
                flash("Incorrect password. Please try again.", "login_error")  # Specific category
                return redirect(url_for("login"))  # Ensure it redirects
        else:
            flash("Username not found. Please register first.", "login_error")  # Specific category
            return redirect(url_for("login"))  # Ensure it redirects

    return render_template("login.html")


@app.route("/sell", methods=["GET", "POST"])
def sell():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})

    if request.method == "POST":
        # Create the uploads directory if it doesn't exist
        uploads_dir = os.path.join("static", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        # Save uploaded images
        image_paths = []
        for i in range(1, 5):
            image_file = request.files.get(f"image{i}")
            if image_file and image_file.filename:
                # Generate a unique filename
                filename = f"{session['username']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.{image_file.filename.split('.')[-1]}"
                filepath = os.path.join(uploads_dir, filename)
                image_file.save(filepath)
                image_paths.append(f"static/uploads/{filename}")
            else:
                image_paths.append(None)

        # Prepare product data
        product_data = {
            "username": session["username"],
            "name": request.form["name"],
            "category": request.form["category"],
            "description": request.form["description"],
            "image1": image_paths[0],
            "image2": image_paths[1],
            "image3": image_paths[2],
            "image4": image_paths[3],
            "price": int(request.form["price"]),
            "age_group": request.form["age_group"],
            "status": "Pending"
        }

        # Insert product into the database
        product_id = mongo.db.sell_requests.insert_one(product_data).inserted_id

        # Update the user's sold products list
        mongo.db.users.update_one(
            {"username": session["username"]},
            {"$push": {"sold_products": str(product_id)}}
        )

        flash("Product submitted for review!", "success")
        return redirect(url_for("home"))

    return render_template("sell.html", user=user)
@app.route("/my_products")
def my_products():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    sold_product_ids = user.get("sold_products", [])

    pending_products = list(mongo.db.sell_requests.find({"username": session["username"], "status": "Pending"}))
    
    sold_products = []
    for product_id in sold_product_ids:
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        if product:
            sold_products.append(product)

    return render_template("my_products.html", user=user, pending_products=pending_products, sold_products=sold_products)
@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            flash("Product not found!", "error")
            return redirect(url_for("home"))

        seller = mongo.db.users.find_one({"username": product["username"]})
        seller_name = seller["username"] if seller else "Unknown"

        user = None
        if "username" in session:
            user = mongo.db.users.find_one({"username": session["username"]})

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("home"))
    
    return render_template('product_detail.html', product=product, seller_name=seller_name, user=user)

# Admin Review Products Route
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
            # Check if there's an approved negotiation for this product
            negotiation = mongo.db.negotiations.find_one({
                "product_id": str(product["_id"]),
                "buyer": session["username"],
                "status": "Approved"
            })

            # Use the negotiated price if available, otherwise use the product price
            price = negotiation["proposed_price"] if negotiation else product["price"]

            product["price"] = price  # Update the price in the product details
            product["quantity"] = item["quantity"]
            cart_items.append(product)
            total_cost += price * item["quantity"]  # Update total cost

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



@app.route("/purchased_items")
def purchased_items():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    purchase_history = user.get("purchase_history", [])

    return render_template("purchased_items.html", purchase_history=purchase_history, user=user)

@app.route("/checkout", methods=["POST"])
def checkout():
    if "username" not in session:
        return redirect(url_for("login"))

    user = mongo.db.users.find_one({"username": session["username"]})
    cart = mongo.db.carts.find_one({"username": session["username"]})

    if not cart or "items" not in cart or len(cart["items"]) == 0:
        return redirect(url_for("cart"))

    # Calculate total cost
    total_cost = 0
    for item in cart["items"]:
        product = mongo.db.products.find_one({"_id": ObjectId(item["_id"])})
        if product:
            # Check if there's an approved negotiation for this product
            negotiation = mongo.db.negotiations.find_one({
                "product_id": str(product["_id"]),
                "buyer": session["username"],
                "status": "Approved"
            })

            # Use the negotiated price if available, otherwise use the product price
            price = negotiation["proposed_price"] if negotiation else product["price"]
            total_cost += item["quantity"] * price
        else:
            # If the product is not found, remove it from the cart
            cart["items"].remove(item)
            mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": cart["items"]}})
            flash(f"Product with ID {item['_id']} no longer exists and has been removed from your cart.", "warning")

    # Check if user has enough coins
    if user["coins"] < total_cost:
        flash("⚠️ Not enough coins to complete the purchase. Earn more coins and try again.", "error")
        return redirect(url_for("cart"))

    # Deduct coins from the buyer
    mongo.db.users.update_one({"username": session["username"]}, {"$inc": {"coins": -total_cost}})

    # Save purchase history and remove products from the products collection
    purchase_history = []
    for item in cart["items"]:
        product = mongo.db.products.find_one({"_id": ObjectId(item["_id"])})
        if product:
            # Check if there's an approved negotiation for this product
            negotiation = mongo.db.negotiations.find_one({
                "product_id": str(product["_id"]),
                "buyer": session["username"],
                "status": "Approved"
            })

            # Use the negotiated price if available, otherwise use the product price
            price = negotiation["proposed_price"] if negotiation else product["price"]

            # Add product to purchase history
            purchase_history.append({
                "product_id": product["_id"],
                "name": product["name"],
                "category": product.get("category", "Uncategorized"),  # Ensure category exists
                "price": price,  # Use the negotiated price
                "quantity": item["quantity"],
                "purchase_date": datetime.utcnow()  # Correct usage of datetime
            })

            # Update the seller's coins
            seller = mongo.db.users.find_one({"username": product["username"]})
            if seller:
                mongo.db.users.update_one(
                    {"username": product["username"]},
                    {"$inc": {"coins": price * item["quantity"]}}
                )

                # Add a notification for the seller
                notification_message = f"Your product {product['name']} has been sold to {session['username']} for {price * item['quantity']} coins. Your new balance is {seller['coins'] + price * item['quantity']} coins."
                mongo.db.notifications.insert_one({
                    "receiver": product["username"],
                    "message": notification_message,
                    "status": "unread",
                    "date": datetime.now()
                })

            # Remove the product from the products collection
            mongo.db.products.delete_one({"_id": ObjectId(item["_id"])})

    # Update user's purchase history
    mongo.db.users.update_one(
        {"username": session["username"]},
        {"$push": {"purchase_history": {"$each": purchase_history}}}
    )

    # Clear the cart after checkout
    mongo.db.carts.update_one({"username": session["username"]}, {"$set": {"items": []}})

    flash("Checkout successful! Thank you for your purchase.", "success")
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

    # Fetch the negotiation details
    negotiation = mongo.db.negotiations.find_one({"_id": ObjectId(negotiation_id)})
    if not negotiation:
        flash("Negotiation not found.", "error")
        return redirect(url_for("my_negotiations"))

    # Fetch the product details
    product = mongo.db.products.find_one({"_id": ObjectId(negotiation["product_id"])})
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("my_negotiations"))

    # Update the negotiation status to "Approved"
    mongo.db.negotiations.update_one(
        {"_id": ObjectId(negotiation_id)},
        {"$set": {"status": "Approved"}}
    )

    # Add the product to the buyer's cart with the negotiated price
    buyer_cart = mongo.db.carts.find_one({"username": negotiation["buyer"]})
    if not buyer_cart:
        # Create a new cart for the buyer if it doesn't exist
        mongo.db.carts.insert_one({"username": negotiation["buyer"], "items": []})
        buyer_cart = mongo.db.carts.find_one({"username": negotiation["buyer"]})

    # Check if the product is already in the buyer's cart
    product_in_cart = False
    for item in buyer_cart["items"]:
        if str(item["_id"]) == str(negotiation["product_id"]):
            product_in_cart = True
            break

    if not product_in_cart:
        # Add the product to the buyer's cart
        mongo.db.carts.update_one(
            {"username": negotiation["buyer"]},
            {"$push": {"items": {"_id": ObjectId(negotiation["product_id"]), "quantity": 1}}}
        )

    # Add a notification for the buyer
    notification_message = f"Your negotiation for {product['name']} has been approved. The price is now {negotiation['proposed_price']} coins."
    mongo.db.notifications.insert_one({
        "receiver": negotiation["buyer"],
        "message": notification_message,
        "status": "unread",
        "date": datetime.now()
    })

    flash(f"Negotiation for {product['name']} approved! Price is now {negotiation['proposed_price']} coins.", "success")
    return redirect(url_for("my_negotiations"))

@app.route("/reject_negotiation/<negotiation_id>")
def reject_negotiation(negotiation_id):
    if "username" not in session:
        return redirect(url_for("login"))

    # Fetch the negotiation details
    negotiation = mongo.db.negotiations.find_one({"_id": ObjectId(negotiation_id)})
    if not negotiation:
        flash("Negotiation not found.", "error")
        return redirect(url_for("my_negotiations"))

    # Update the negotiation status to "Rejected"
    mongo.db.negotiations.update_one(
        {"_id": ObjectId(negotiation_id)},
        {"$set": {"status": "Rejected"}}
    )

    # Add a notification for the buyer
    notification_message = f"Sorry, your negotiation for {negotiation['product_name']} has been rejected. The seller found the proposed price too low."
    mongo.db.notifications.insert_one({
        "receiver": negotiation["buyer"],
        "message": notification_message,
        "status": "unread",
        "date": datetime.now()
    })

    flash("Negotiation rejected.", "error")
    return redirect(url_for("my_negotiations"))

@app.route("/notifications")
def notifications():
    if "username" not in session:
        return redirect(url_for("login"))

    # Fetch all notifications for the logged-in user
    notifications = list(mongo.db.notifications.find({"receiver": session["username"]}).sort("date", -1))
    
    # Mark all notifications as "read"
    mongo.db.notifications.update_many(
        {"receiver": session["username"], "status": "unread"},
        {"$set": {"status": "read"}}
    )

    # Count unread notifications for the header
    unread_notifications = mongo.db.notifications.count_documents({
        "receiver": session["username"],
        "status": "unread"
    })

    # Fetch the logged-in user's data (including coins)
    user = mongo.db.users.find_one({"username": session["username"]})

    return render_template(
        "notifications.html",
        notifications=notifications,
        unread_notifications=unread_notifications,
        user=user,  # Pass user data to the template
    )


@app.context_processor
def inject_unread_notifications():
    if "username" in session:
        unread_notifications = mongo.db.notifications.count_documents({
            "receiver": session["username"],
            "status": "unread"
        })
        return {"unread_notifications": unread_notifications}
    return {"unread_notifications": 0}

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("admin", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
