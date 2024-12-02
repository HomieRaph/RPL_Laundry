import hashlib
from flask import  Blueprint, session, render_template, request, redirect, jsonify
from datetime import datetime, timedelta, timezone
from model import verify_login_admin, app, register_admin, Laundry, db, Member, get_all_orders, get_all_members
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

admin = Blueprint('admin', __name__)

@admin.route('/')
def admin_page():
    if not verify_token(session.get('access_token')):
        return redirect('/admin/logout')
    # orders = Laundry.query.join(Member).add_columns(
    #     Laundry.order_id,
    #     Member.name.label('customer_name'),
    #     Laundry.service,
    #     Laundry.qty,
    #     Laundry.date,
    #     Laundry.status
    # ).all()

    temp = []
    orders = Laundry.query.all()
    
    for order in orders:
        print(order.member.name)
        temp.append(
            {
                'order_id': order.order_id,
                'customer_name': order.member.name,
                'service': order.service.service_name,
                'qty': order.qty,
                'date': order.date,
                'status': order.status
            }
        )
    print(orders)
    return render_template('admin.html', orders=temp)

@admin.route('/login', methods=['GET', 'POST'])
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
                {
                    'exp': utc_now + timedelta(minutes=30), 
                    'sub': res.name,
                    'id' : res.admin_id,
                    'role': 'admin'
                }, 
                app.secret_key, algorithm='HS256')
            session['access_token'] = encoded_jwt
            return redirect('/admin')
    return render_template('admin_login.html')

@admin.route('/logout')
def logout():
    session.pop('access_token', None) 
    return redirect('/admin/login')
    
@admin.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['register-email']
        password = request.form['register-password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        name = request.form['name']         
        res = register_admin(email, hashed_password, name)

        if res:
            return redirect('/admin/login')
    if verify_token(session.get('access_token')):
        return redirect('/admin')
    return render_template('admin_login.html')

@app.route("/update_status", methods=["POST"])
def update_status():
    order_id = request.form.get("order_id")
    new_status = request.form.get("status")

    order = Laundry.query.get(order_id)
    if order:
        order.status = new_status
        db.session.commit()
    return redirect('admin')

@app.route('/admin/customers')
def manage_customers():
    customers = get_all_members()
    return render_template('customers.html', customers=customers)

@app.route('/admin/customers/<int:member_id>', methods=['GET'])
def get_customer_details(member_id):
    customer = Member.query.get_or_404(member_id)
    transactions = Laundry.query.filter_by(member_id=member_id).all()
    transaction_data = [
        {
            "order_id": t.order_id,
            "service_name": t.service.service_name,
            "qty": t.qty,
            "status": t.status,
            "date": t.date.strftime('%Y-%m-%d')
        }
        for t in transactions
    ]
    return jsonify({
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "transactions": transaction_data
    })

@app.route('/admin/reports', methods=['GET'])
def revenue_report():
    transactions = Laundry.query.all()
    total_revenue = sum([t.qty * t.service.service_price for t in transactions])

    transaction_data = [
        {
            "order_id": t.order_id,
            "customer_name": t.member.name,
            "service_name": t.service.service_name,
            "qty": t.qty,
            "total": t.qty * t.service.service_price,
            "status": t.status,
            "date": t.date.strftime('%Y-%m-%d')
        }
        for t in transactions
    ]

    return render_template('reports.html', total_revenue=total_revenue, transactions=transaction_data)
