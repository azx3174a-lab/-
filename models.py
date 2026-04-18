from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_name = db.Column(db.String(100))
    price = db.Column(db.Float)
    expiry_date = db.Column(db.String(20))

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_icon_url = db.Column(db.String(500), default="https://cdn-icons-png.flaticon.com/512/5968/5968269.png")
