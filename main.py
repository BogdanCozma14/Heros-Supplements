from flask import Flask, flash, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
import os
from datetime import timedelta


# app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=48)
# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:postgres@localhost/supplements'
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy(app)
Session(app)



# Defininig the model class for users table
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    # defining the relanshionship with products many to many through cart
    products = db.relationship("Product", secondary="carts", back_populates="users")
    # defining the relanshionship with the carts
    carts = db.relationship("Cart", back_populates="user")


# Defining the model class for products table
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key = True)
    url_image = db.Column(db.String(255))
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    # relanshionship with users
    # users = db.relationship("User", secondary=cart_association, back_populates="products")
    users = db.relationship("User", secondary="carts", back_populates="products")
    carts = db.relationship("Cart", back_populates="product")


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    temp_user_id = db.Column(db.Text)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1)
    total = db.Column(db.Float)

    # Define relationships
    user = db.relationship("User", back_populates="carts")
    product = db.relationship("Product", back_populates="carts")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def generate_temporary_user_id():
    # unique temporary id for someone who is not logged in
    return str(uuid.uuid4())


# Get the cart count of the user (logged in or not)
def get_cart_count():
    if 'user_id' in session:
        user_id = session['user_id']
        temp_user_id = None
    else:
        if 'temp_user_id' not in session:
            session['temp_user_id'] = generate_temporary_user_id()
        user_id = None
        temp_user_id = session['temp_user_id']
    
    cart_count = Cart.query.filter((Cart.user_id == user_id) | (Cart.temp_user_id == temp_user_id)).count()
    return cart_count


@app.route("/")
def index():
    # getting all the products and group them by category
    products = Product.query.all()
    products_by_category = {}
    cart_count = get_cart_count()
    for product in products:
        if product.category not in products_by_category:
            products_by_category[product.category] = []
        products_by_category[product.category].append(product)
    return render_template("index.html", products_by_category=products_by_category, cart_count=cart_count)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/products", defaults={'page': 1})
@app.route("/products/<int:page>")
def display_products(page):
    cart_count = get_cart_count()
    products_per_page = 15
    offset = (page - 1) * products_per_page
    # Get the selected category by the user
    selected_category = request.args.get("category", "All")
    # Query the database to fetch products for the current page using the offset and the selected category
    if selected_category == "All":
        products = products = Product.query.offset(offset).limit(products_per_page).all()
        # total number of products
        total_products = Product.query.count()
    else:
        products = Product.query.filter_by(category=selected_category).offset(offset).limit(products_per_page).all()
        # total number of products
        total_products = Product.query.filter_by(category=selected_category).count()

    # Calculate the total number of pages
    total_pages = (total_products + products_per_page - 1) // products_per_page

    return render_template("products.html", products=products, page=page, total_pages=total_pages, selected_category=selected_category, cart_count=cart_count)


@app.route("/about")
def about():
    cart_count = get_cart_count()
    return render_template("about.html", cart_count=cart_count)


@app.route("/contact")
def contact():
    cart_count = get_cart_count()
    return render_template("contact.html", cart_count=cart_count)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # the user will be kept loggged in
            session["user_id"] = user.id
            flash("You logged into your account", "success")
            return redirect("/")
        else:
            flash("Your email and password don't match. Please try again")
            return render_template("login.html")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # getting the fields
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        if len(username) < 3:
            flash("The username is too short (the minimum is 3 characters)", "error")
            return render_template("register.html")
        if len(password) < 5:
            flash("The password is too short (the minimum is 5 characters)", "error")
            return render_template("register.html")
        # check if the username or email were already used by someone else
        # generate a password hash
        hashed_password = generate_password_hash(password)
        # Creating a user object with the data from the registration
        new_user = User(username=username, email=email, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created", "success")
            return redirect("/login")
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists. Please choose another.")
            return render_template("register.html")
    return render_template("register.html")


# adding to cart functionality
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    # checks if the user is logged into his account
    if 'user_id' in session:
        user_id = session['user_id']
        temp_user_id = None
    else:
        if 'temp_user_id' not in session:
            session['temp_user_id'] = generate_temporary_user_id()
        user_id = None
        temp_user_id = session['temp_user_id']
        # check if the product exists
    product = Product.query.get(product_id)
    if product:
        # Check if the product is already in the user's cart
        existing_cart_item = Cart.query.filter(
            ((Cart.user_id == user_id) | (Cart.temp_user_id == temp_user_id)) & (Cart.product_id == product.id)
        ).first() 
        if existing_cart_item:
            # If the product is in the cart, increment the quantity
            existing_cart_item.quantity += 1
            # Update the total price for the cart item
            existing_cart_item.total = round(existing_cart_item.quantity * product.price, 2)
            db.session.commit()
        else:
            # If not, create a new cart item with a quantity of 1
            cart_item = Cart(user_id=user_id, temp_user_id=temp_user_id, product_id=product.id, total=product.price)
            db.session.add(cart_item)
            db.session.commit()
            # user_cart = Cart.query.filter_by(user_id=user_id).all()
            user_cart = Cart.query.filter((Cart.user_id == user_id) | (Cart.temp_user_id == temp_user_id)).all()
            total_cart_price = sum(cart_item.total for cart_item in user_cart)
            # Update the user's cart total_price
            if user_id:
                user = User.query.get(user_id)
                user.cart_total_price = total_cart_price
                db.session.commit()

            flash("Item added to the cart", "success")
    else:
        flash("Product not found!", "error")
    return redirect("/")


# removing from cart functionality
@app.route("/remove_from_cart/<int:cart_item_id>")
def remove_from_cart(cart_item_id):
    if "user_id" in session:
        user_id = session["user_id"]
        temp_user_id = None
    elif 'temp_user_id' in session:
        user_id = None
        temp_user_id = session['temp_user_id']
    else:
        flash("you are not logged in", "error")
        return redirect("/")
    cart_item = Cart.query.get(cart_item_id)
    if cart_item:
        if cart_item.user_id == user_id or cart_item.temp_user_id == temp_user_id:
            # removing the product from the cart
            db.session.delete(cart_item)
            db.session.commit()
            flash("Item removed from the cart", "success")
        else:
            flash("You don't have permission to remove this item", "error")
    else:
        flash("Item not found in the cart", "error")

    return redirect("/cart")
   

@app.route("/cart")
def cart():
    if 'user_id' in session:
        user_id = session['user_id']
        temp_user_id = None
        user_cart = Cart.query.filter((Cart.user_id == user_id) | (Cart.temp_user_id == temp_user_id)).all()
        total_cart_price = round(sum(cart_item.total for cart_item in user_cart), 2)
    else:
        if 'temp_user_id' not in session:
            session['temp_user_id'] = generate_temporary_user_id()
        user_id = None
        temp_user_id = session['temp_user_id']
        user_cart = Cart.query.filter((Cart.user_id == user_id) | (Cart.temp_user_id == temp_user_id)).order_by(Cart.id).all()
        total_cart_price = round(sum(cart_item.total for cart_item in user_cart), 2)

    cart_count = len(user_cart) if user_cart else 0

    return render_template("cart.html", cart_items=user_cart, total_cart_price=total_cart_price, cart_count=cart_count)


# changing the quantity of the products with incremending/decrementing buttons
@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    cart_item_id = request.form.get('cart_item_id')
    new_quantity = int(request.form.get('new_quantity'))
    # get the cart item that has its quantity changed
    cart_item = Cart.query.get(cart_item_id)
    # getting the product that has its quantity changed in the cart
    product = Product.query.get(cart_item.product_id)
    
    if cart_item:
        cart_item.quantity = new_quantity
        cart_item.total = new_quantity * product.price
        db.session.commit()
        return jsonify({'message': 'Quantity updated successfully'})
    else:
        return jsonify({'error': 'Cart item not found'})
    

# receiving the form from the contact page to the email
@app.route("/form", methods=["POST"])
def form():
    flash("Your form was sent succesfully")
    return redirect("/contact")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    flash("Thank you for subscribing to the Newsletter!")
    return redirect("/")


if __name__ == '__main__':
    # create tables if they don't exists
    with app.app_context():
        db.create_all()
    app.run()
