import datetime 
from extensions import db
from flask_login import UserMixin, current_user
from sqlalchemy import DateTime


# User creation
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    confirm_email = db.Column(db.Boolean, default=False)
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)

