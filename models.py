from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Table name in the database
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each user
    username = db.Column(db.String(150), nullable=False, unique=True)  # Username field
    email = db.Column(db.String(150), nullable=False, unique=True)  # Email field
    password = db.Column(db.String(200), nullable=False)  # Password field (hashed)
    otp_secret = db.Column(db.String(16))  # Secret key for 2FA
    consent = db.Column(db.Boolean, default=False)  
