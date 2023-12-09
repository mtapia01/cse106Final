from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import os

UPLOAD_FOLDER = 'uploads'


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Update with your database URI
app.config['SECRET_KEY'] = 'key'  # Update with your secret key
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = './uploads/'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}



# def load_user(user_id):
#     return User.query.get(int(user_id))
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140), nullable=False)
    image = db.Column(db.String(255))  # Store the file path or URL
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.content}', '{self.date_posted}')"

    def save_picture(self, picture):
        # Save the picture to the server's static folder
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture.filename)
        picture.save(picture_path)

        # Set the image field in the Post model to the filename
        self.image = picture.filename

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

#is_authenticated
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # posts = db.relationship('Post', backref='author', lazy=True)

    def get_id(self):
        return str(self.id)  # Assuming `id` is your user ID field
    #hashes password with salt
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #checks hashed passwords
    def check_password(self, password):
        return check_password_hash(self.password, password)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

# Pages
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
@app.route('/feed')
@login_required
def feed():
    return render_template('/feed.html')
@app.route('/create-post')
@login_required
def create_post_form():
    return render_template('upload.html')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Functions
@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    # Get the file and other form data
    picture = request.files['picture']
    content = request.form['content']
    # Get the logged-in user's ID
    user_id = current_user.id

    # Check if the file is allowed
    if picture and allowed_file(picture.filename):
        try:
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H')
            unique_filename = f"{timestamp}_{secure_filename(picture.filename)}"
            # picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # Save the picture to the server's static folder
            picture.save(picture_path)

            # Create a new Post instance and set its attributes
            new_post = Post(content=content, image=picture_path, user_id=user_id)

            # Add and commit the new_post to the database
            db.session.add(new_post)
            db.session.commit()

            return jsonify({'message': 'Post created successfully'})
        except Exception as e:
            return jsonify({'error': f'Error creating post: {str(e)}'})
    else:
        return jsonify({'error': 'Invalid file format'})

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

@app.route('/get_current_user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({'user_id': current_user.id})

@app.route('/login', methods=['POST'])
def login():
    # username = request.form.get('username')
    # password = request.form.get('password')

    data = request.get_json()
    username = data['username']
    password = data['password']

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400


    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Login successful
        # session['user_id'] = user.id
        login_user(user) 
        return jsonify({'message': 'Login successful', 'user': {'username': user.username}})
    else:
        # Invalid username or password
        return jsonify({'error': 'Invalid username or password'}), 401
    
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200
    


@app.route('/dashboardFeed', methods=['GET'])
@login_required
def dashboardFeed():
    user_id = session.get('_user_id')

    # print('followed_user_ids:', followed_user_ids)
    # print('feed_posts:', feed_posts)
    userName = user_id
    if user_id:
        # Retrieve all posts with the given user_id
        posts = Post.query.filter_by(user_id=user_id).all()
        # userName = User.query.filter_by(user_id=user_id).first()

        # Convert posts to a format that can be easily serialized to JSON
        serialized_posts = [
            {
                'content': post.content,
                'image': post.image,
                'date_posted': post.date_posted,
                'user': userName
            }
            for post in posts
        ]

        return jsonify(serialized_posts)


    return jsonify({'error': 'User not authenticated'}), 401


if __name__ == '__main__':
    app.run(debug=True)


