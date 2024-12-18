from flask import Flask, jsonify, make_response, session, render_template, request, render_template_string, redirect, Blueprint, abort, send_from_directory
import hashlib
from datetime import datetime, timedelta, timezone
from model import *
from controllers.auth import auth, verify_token
from controllers.member import member
from controllers.admin import admin
from env import app_secret_key
import jwt
import os


app.secret_key = app_secret_key

@app.route('/assets/<path:filename>')
@app.route('/<path:route>/assets/<path:filename>')
def serve_assets(filename, route=None):
    # print(filename, app.root_path)
    assets_dir = os.path.join(app.root_path, 'assets')
    return send_from_directory(assets_dir, filename)

@app.route('/')
def main(): 
    # render_template('index.html')
    return render_template('index.html')

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(member, url_prefix='/member')
app.register_blueprint(admin, url_prefix='/admin')

@app.route('/home')
def home_page():
    if verify_token(session.get('access_token')):
        return render_template('index.html')
    return redirect('/member/logout')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/services')
def services_page():
    return render_template('services.html')

@app.route('/book')
def contact_page():
    if verify_token(session.get('access_token')):
        all_services = get_all_services()
        return render_template('book.html', all_services=all_services)
    return redirect('/member/logout')

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
