from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)

    dishes = db.relationship('Dish', back_populates='category', order_by='Dish.name')

    def __repr__(self):
        return f"<Category {self.name}>"

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(130), unique=True, nullable=False)
    passwrod_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable = False)
    def set_password(self, password):
        self.passwrod_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwrod_hash, password)


class Dish(db.Model):
    __tablename__ = 'dishes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False, default='')
    price = db.Column(db.Integer, nullable=False)
    emoji = db.Column(db.String(8), nullable=False, default='🍽️')
    is_available = db.Column(db.Boolean, nullable=False, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', back_populates='dishes')

    def __repr__(self):
        return f"<Dish {self.name} {self.price} грн>"


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Доставляємо якнайшвидше! 🛵", nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=True)
    dish = db.relationship('Dish', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.id} for {self.full_name}>"