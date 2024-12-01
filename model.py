from flask import Flask, jsonify, make_response, session, render_template, request, render_template_string, redirect, Blueprint, abort
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import TIMESTAMP
import pytz

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:JAWPYaxgaBIQABYTToJXWyJmPzOlmWwE@junction.proxy.rlwy.net:50607/railway'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/rpl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column('admin_id', db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100), unique=True)
    
    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

class Member(db.Model):
    __tablename__ = "member"

    member_id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    
    # One-to-Many relationship with the Address table
    addresses = db.relationship('Address', back_populates='member', cascade="all, delete-orphan")
    
    
    def __init__(self, phone, name, email, password):
        self.phone = phone
        self.name = name
        self.email = email
        self.password = password
        # self.member_type = member_type
        # self.counter = counter
        # self.last_attendance = last_attendance

class Address(db.Model):
    __tablename__ = "address"

    address_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    
    # Relationship back to Member
    member = db.relationship('Member', back_populates='addresses')

    def __init__(self, member_id, address):
        self.member_id = member_id
        self.address = address


def verify_login_admin(email, password):
    admin = Admin.query.filter(Admin.email == email, Admin.password == password).first()
    if admin is None:
        return False
    return admin

def verify_login_member(email, password):
    member = Member.query.filter(Member.email == email, Member.password == password).first()
    if member is None:
        return False
    return member

def register_admin(email, password, name):
    user = Admin(email=email, password=password, name=name)
    try:
        db.session.add(user)
        db.session.commit()
        return True
    except IntegrityError as e:
        db.session.rollback()  # Rollback to reset the session
        error_message = str(e.orig)  # Capture the original error message
        # print(error_message)
        # Extract the column name (key) causing the duplicate entry error
        if "Duplicate entry" in error_message:
            # The column name appears after 'for key'
            error_message = error_message.split("for key ")[-1].split("'")[1]
            print(f"Error: Duplicate entry for column '{error_message}'")
        return False, error_message
    except:
        abort(500)

def register_member(phone, name, email, password):
    user = Member(phone=phone, name=name, email=email, password=password)
    try:
        db.session.add(user)
        db.session.commit()
        return True
    except IntegrityError as e:
        db.session.rollback()  # Rollback to reset the session
        error_message = str(e.orig)  # Capture the original error message
        # print(error_message)
        # Extract the column name (key) causing the duplicate entry error
        if "Duplicate entry" in error_message:
            # The column name appears after 'for key'
            error_message = error_message.split("for key ")[-1].split("'")[1]
            print(f"Error: Duplicate entry for column '{error_message}'")
        return False, error_message
    except:
        abort(500)

def get_all_members():
    member = Member.query.all()
    response = []
    for i in member:
        response.append({
            "member_id": i.member_id,
            "phone": i.phone,
            "name": i.name
        })
    return response

def get_member_by_phone(phone):
    member = Member.query.filter(Member.phone == phone).first()
    return member

def get_members(member_id):
    member = Member.query.filter(Member.member_id == member_id).first() 
    return member



