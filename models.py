# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # store hashed password
    role = db.Column(db.String(20), nullable=False, default=Role.STAFF.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(150))
    email = db.Column(db.String(150))
    address = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Transaction', backref='supplier', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=0)
    description = db.Column(db.String(500))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    qty = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'in' or 'out' or 'order'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(500))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)

    product = db.relationship('Product', backref='transactions')
    user = db.relationship('User', backref='transactions')
