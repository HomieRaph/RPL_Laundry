# import hashlib
# from flask import  Blueprint, session, render_template, request, redirect
# from datetime import datetime, timedelta, timezone
# from model import *
# from controllers.auth import verify_token
# import jwt
# # import qrcode
# member = Blueprint('member', __name__)

# @member.route('/', methods=['GET', 'POST'])
# def member_page():
#     if not verify_token(session.get('access_token')):
#         return redirect('/auth/logout')
    
#     if request.method == 'POST':
#         name = request.form['name']
#         phone = request.form['phone']
#         member_type = request.form['member_type']      
#         utc_now = datetime.now(timezone.utc)
#         jakarta_time = utc_now + timedelta(hours=7)    
#         # datetime.datetime.utcnow()
#         res = register_member(phone, name, member_type, 0, jakarta_time)
#         if res:
#             return redirect('/member?message=success')
#             # member telah di daftarkan
#         else:
#             return redirect('/member?message=failed')
            
        
#     all_member = get_all_members()
#     # print(all_member)
#     message = request.args.get('message')
#     return render_template("member.html", all_member=all_member, message=message)





import hashlib
from flask import  Blueprint, session, render_template, request, redirect, jsonify
from datetime import datetime, timedelta, timezone
from model import verify_login_member, app, register_member, get_cart_item, Member, Laundry, Address, db, delete_cart_item, Cart, Service, add_cart_item
import jwt

def verify_token(token):
    try:
        jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidSignatureError:
        return False
    except:
        return False


member = Blueprint('member', __name__)

@member.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        res = verify_login_member(email, hashed_password)

        if res:
            utc_now = datetime.now(timezone.utc)
            # print(res)
            encoded_jwt = jwt.encode(
                {
                    'exp': utc_now + timedelta(minutes=30), 
                    'sub': res.name,
                    'id' : res.member_id,
                    'role': 'member'
                }, 
                app.secret_key, algorithm='HS256')
            session['member_id'] = res.member_id
            session['access_token'] = encoded_jwt
            return redirect('/home')

    return render_template('member_login.html')

@member.route('/logout')
def logout():
    session.pop('access_token', None) 
    return redirect('/member/login')
    
@member.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        name = request.form['name']         
        email = request.form['register-email']
        password = request.form['register-password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        print(phone, name, email, hashed_password)
        res = register_member(phone, name, email, hashed_password)

        if res:
            return redirect('/member/login')
    if verify_token(session.get('access_token')):
        return redirect('/home')
    return render_template('member_login.html')

@member.route('/cart')
def cart():
    if not verify_token(session.get('access_token')):
        return redirect('/member/logout')
    
    encoded_jwt = session.get('access_token')
    try:
        decoded_jwt = jwt.decode(encoded_jwt, app.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect('/member/logout')
    except jwt.InvalidTokenError:
        return redirect('/member/logout')
    
    member_id = decoded_jwt['id']
    cart, total_price = get_cart_item(member_id)
    services = Service.query.all()
    
    return render_template('cart.html', cart=cart, total_price=total_price, services=services)


@member.route('/my')
def user_page():
    if not verify_token(session.get('access_token')):
        return redirect('/member/logout')

    encoded_jwt = session.get('access_token')
    try:
        decoded_jwt = jwt.decode(encoded_jwt, app.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect('/member/logout')
    except jwt.InvalidTokenError:
        return redirect('/member/logout')

    member_id = decoded_jwt['id']
    
    if member_id:
        #  Member.query.filter(Member.phone == phone).first()
        member = Member.query.filter(Member.member_id == member_id).first()
        if not member:
            return redirect('/member/logout')

        history = Laundry.query.filter(member_id == member_id).all()
        address = Address.query.filter(member_id == member_id).first()

        print(member.address[0].address)

        print(history)
        return render_template('user.html', member=member, history=history, address=address)
    
    return redirect('/member/logout')

@member.route('/edit', methods=['GET', 'POST'])
def edit():
    if not verify_token(session.get('access_token')):
        return redirect('/member/logout')
    
    encoded_jwt = session.get('access_token')
    try:
        decoded_jwt = jwt.decode(encoded_jwt, app.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect('/member/logout')
    except jwt.InvalidTokenError:
        return redirect('/member/logout')
    
    member_id = decoded_jwt['id']
    member = Member.query.get(member_id)
    address = Address.query.filter_by(member_id=member_id).first()  # Get the member's address
    
    if request.method == 'POST':
        # Update member details
        member.name = request.form['name']
        if request.form['password']:  # Only update if the password is provided
            member.password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()

        # Update address
        if address:
            address.address = request.form['address']  # Update existing address
        else:
            # If address doesn't exist, create a new one
            new_address = Address(member_id=member_id, address=request.form['address'])
            db.session.add(new_address)
        db.session.commit()
        return redirect('/member/my')

    return render_template('edit.html', member=member, address=address)

@member.route('/cart/delete', methods=['POST'])
def delete_item():
    if not verify_token(session.get('access_token')):
        return redirect('/member/logout')
    
    data = request.get_json()
    item_id = data.get('item_id')
    
    res = delete_cart_item(cart_id=item_id)
    
    if res:
        return jsonify({'status': 'success'})
    return jsonify({'status': 'failed'})
    
@member.route('/cart/add', methods=['POST'])
def add_item():
    if not verify_token(session.get('access_token')):
        return redirect('/member/logout')
    
    data = request.get_json()
    service_id = data.get('service_id')
    qty = data.get('qty')
    express = data.get('express')
    
    encoded_jwt = session.get('access_token')
    try:
        decoded_jwt = jwt.decode(encoded_jwt, app.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect('/member/logout')
    except jwt.InvalidTokenError:
        return redirect('/member/logout')
    
    member_id = decoded_jwt['id']
    print(service_id, qty, express, data, type(express))
    
    try:
        if express:
            service_id += 6
        
        res = add_cart_item(member_id=member_id, service_id=service_id, qty=qty)
        return jsonify({'status': 'success'})
    except:
        # db.session.rollback()
        return jsonify({'status': 'failed'})

@member.route('/cart/update', methods=['POST'])
def update_item():
    if not verify_token(session.get('access_token')):
        return redirect('/member/logout')
    
    data = request.get_json()
    item_id = data.get('item_id')
    qty = data.get('qty')
    
    try:
        cart = Cart.query.get(item_id)
        cart.qty = qty
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except:
        db.session.rollback()
        return jsonify({'status': 'failed'})



@member.route('/cart/checkout')
def checkout_page():
    if not verify_token(session.get('access_token')):
        return redirect('/member/logout')
    
    encoded_jwt = session.get('access_token')
    try:
        decoded_jwt = jwt.decode(encoded_jwt, app.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect('/member/logout')
    except jwt.InvalidTokenError:
        return redirect('/member/logout')
    
    member_id = decoded_jwt['id']
    member = Member.query.get(member_id)
    address = member.address[0].address
    cart, total_price = get_cart_item(member_id)
    
    
    # for item in cart:
    #     laundry = Laundry(member_id=member_id, service_id=item['service_id'], qty=item['qty'])
    #     db.session.add(laundry)
    # db.session.commit()
    
    # print(cart)
    
    return render_template('checkout.html', member=member, address=address, cart=cart, total_price=total_price)


@member.route('/checkout', methods=['POST'])
def check_out():
    if not verify_token(session.get('access_token')):
        return redirect('/member/logout')
    
    encoded_jwt = session.get('access_token')
    try:
        decoded_jwt = jwt.decode(encoded_jwt, app.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return redirect('/member/logout')
    except jwt.InvalidTokenError:
        return redirect('/member/logout')
    
    member_id = decoded_jwt['id']
    member = Member.query.get(member_id)
    cart, total_price = get_cart_item(member_id)
    
    for item in cart:
        print(item)
        laundry = Laundry(member_id=member_id, service_id=item['service_id'], qty=item['qty'])
        db.session.add(laundry)
        cart_item = Cart.query.get(item['id'])
        db.session.delete(cart_item)
    db.session.commit()
    return redirect('/member/my') 

