import hashlib
from flask import  Blueprint, session, render_template, request, redirect
from datetime import datetime, timedelta, timezone
from model import verify_login_admin, app, register_admin 
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


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        res = verify_login_admin(email, hashed_password)

        if res:
            utc_now = datetime.now(timezone.utc)
            # print(res)
            encoded_jwt = jwt.encode(
                {'exp': utc_now + timedelta(minutes=1), 'sub': res.name}, app.secret_key, algorithm='HS256')
            session['access_token'] = encoded_jwt
            return redirect('/home')

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('access_token', None) 
    return redirect('/auth/login')
    
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['register-email']
        password = request.form['register-password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        name = request.form['name']         
        res = register_admin(email, hashed_password, name)

        if res:
            return redirect('/auth/login')
    if verify_token(session.get('access_token')):
        return redirect('/home')
    return render_template('register.html')

    