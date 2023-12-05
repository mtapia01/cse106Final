from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Update with your database URI
app.config['SECRET_KEY'] = 'key'  # Update with your secret key
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140), nullable=False)
    image = db.Column(db.String(255))  # Store the file path or URL
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # used to return a str
    def __repr__(self):
        return f"Post('{self.content}', '{self.date_posted}')"

#is_authenticated
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # posts = db.relationship('Post', backref='author', lazy=True)

    #hashes password with salt
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #checks hashed passwords
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']

    #checking if all info is filled
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    #checking if user is in the table
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username is already taken'}), 400
    
     # Create a new user
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    # new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Signup successful', 'user': {'username': new_user.username}}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    #checking if all info is filled
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    #checking if user is in the table
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        # Redirect the user to a new page after successful login
        return redirect(url_for('dashboard'))   
    else:
        return jsonify({'error': 'Invalid username or password'}), 401



if __name__ == '__main__':
    app.run(debug=True)


