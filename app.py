from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'dbs', 'users.db')
# db = SQLAlchemy(app)



@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/admin')
# def admin():
#     # Fetch all users from the Users table
#     all_users = Users.query.all()
#     return render_template('admin.html', all_users=all_users)


# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form['username']
#     password = request.form['password']
#     user = Users.query.filter_by(username=username, password=password).first()
#     if user:
#         login_user(user)
#         return redirect('/dashboard')  # Redirect to the user's dashboard
#     else:
#         flash('Invalid username or password', 'error')
#         return redirect(url_for('display_login'))

if __name__ == '__main__':
    app.run(debug=True)


# @app.route('/register', methods=['POST'])
# def register():
#     username = request.form['username']
#     password = request.form['password']
#     role = request.form['role']

#     # Check if a user with the same username already exists
#     existing_user = Users.query.filter_by(username=username).first()
#     if existing_user:
#         flash('Username already exists. Please choose a different one.', 'error')
#         return redirect(url_for('display_registration'))

#     # Create a new user and add it to the database
#     new_user = Users(username=username, password=password, role=role)
#     db.session.add(new_user)
#     db.session.commit()

#     flash('Registration successful. You can now log in.', 'success')
#     return redirect(url_for('display_login'))