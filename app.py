from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Category, Dish, User, Order

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trattoria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return redirect(url_for("menu"))


@app.route('/menu')
@app.route('/menu/<slug>')
def menu(slug=None):
    categories = Category.query.order_by(Category.id).all()
    current = None
    query = Dish.query.filter_by(is_available=True)

    if slug:
        current = Category.query.filter_by(slug=slug).first_or_404()
        query = query.filter_by(category_id=current.id)

    q = request.args.get('q', "").strip()
    if q:
        query = query.filter(Dish.name.ilike(f"%{q}%"))

    dishes = query.order_by(Dish.category_id, Dish.name).all()
    return render_template('menu.html', categories=categories, current=current, dishes=dishes, q=q)


@app.route('/dish<int:dish_id>')
def dish_detail(dish_id):
    dish = db.get_or_404(Dish, dish_id)
    return render_template('dish.html', dish=dish)

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', {})
    items = []
    total_price = 0

    for dish_id_str, quantity in cart_items.items():
        dish = db.session.get(Dish, int(dish_id_str))
        if dish:
            subtotal = dish.price * quantity
            total_price += subtotal
            items.append({'dish': dish, 'quantity': quantity, 'subtotal': subtotal})

    return render_template('cart.html', items=items, total_price=total_price)


@app.route('/cart/add/<int:dish_id>', methods=['POST'])
@login_required
def add_to_cart(dish_id):
    dish = db.get_or_404(Dish, dish_id)
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    dish_id_str = str(dish_id)

    if dish_id_str in cart:
        cart[dish_id_str] += 1
    else:
        cart[dish_id_str] = 1

    session.modified = True
    return redirect(request.referrer or url_for('menu'))


@app.route('/cart/remove/<int:dish_id>')
@login_required
def remove_from_cart(dish_id):
    if 'cart' in session:
        dish_id_str = str(dish_id)
        if dish_id_str in session['cart']:
            del session['cart'][dish_id_str]
            session.modified = True
    return redirect(url_for('cart'))

@app.route('/delivery', methods=['GET', 'POST'])
@login_required
def delivery():
    cart_items = session.get('cart', {})
    if not cart_items:
        return redirect(url_for('menu'))

    items = []
    total_price = 0
    for dish_id_str, quantity in cart_items.items():
        dish = db.session.get(Dish, int(dish_id_str))
        if dish:
            subtotal = dish.price * quantity
            total_price += subtotal
            items.append({'dish': dish, 'quantity': quantity, 'subtotal': subtotal})

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        comment = request.form.get('comment', '').strip()

        new_order = Order(
            full_name=full_name,
            phone=phone,
            address=address,
            comment=comment,
            user_id=current_user.id
        )
        db.session.add(new_order)
        db.session.commit()

        session.pop('cart', None)
        return render_template('order_success.html')

    return render_template('delivery.html', items=items, total_price=total_price)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route("/register", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        exist_user = db.session.scalar(db.select(User).where(User.email == email))
        if exist_user:
            return redirect(url_for("registration"))

        new_user = User(username=username, email=email, role="user")
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("menu"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        user = db.session.scalar(db.select(User).where(User.email == email))

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("menu"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("menu"))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)