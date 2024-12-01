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
from flask import  Blueprint, session, render_template, request, redirect
from datetime import datetime, timedelta, timezone
from model import verify_login_member, app, register_member
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
                {'exp': utc_now + timedelta(minutes=1), 'sub': res.name}, app.secret_key, algorithm='HS256')
            session['access_token'] = encoded_jwt
            return redirect('/home')

    return render_template('login.html')

@member.route('/logout')
def logout():
    session.pop('access_token', None) 
    return redirect('/auth/login')
    
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
            return redirect('/auth/login')
    if verify_token(session.get('access_token')):
        return redirect('/home')
    return render_template('login.html')
