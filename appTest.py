from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, Category, Dish, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trattoria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.sesion.get(User, int(user_id))

@app.route("/register", methods=["GET", "POST"])
def registration():
    if request.method == "Post":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        exist_user = db.session.scalar(db.select(User).where(User.email == email))
        if exist_user :
            flash("This user existing")
            return redirect(url_for("registr"))

        new_user = User(username = username, email = email, role = "user")
        new_user.set_password(password)
        db.session.ada(new_user)
        db.session.commit()
        flash("Refister ok")
        return redirect(url_for("login"))


    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()
        user = db.session.scalar(
            db.selcet(User).where(User.email == email)
        )
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("menu"))

    return render_template("login.html")