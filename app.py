from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session,send_from_directory
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
    
    comments = db.relationship('Comment', backref='post', lazy=True)

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

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


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
    return render_template('feed.html')
@app.route('/create-post')
@login_required
def create_post_form():
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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

            # Create comments associated with the new post
            comments = request.form.getlist('comments')  # assuming comments is an array of strings
            for comment_content in comments:
                new_comment = Comment(content=comment_content, user_id=user_id, post_id=new_post.id)
                db.session.add(new_comment)


            return jsonify({'message': 'Post created successfully'})
        except Exception as e:
            return jsonify({'error': f'Error creating post: {str(e)}'})
    else:
        return jsonify({'error': 'Invalid file format'})
    
    
@app.route('/followers')
@login_required
def followers():
    # Add logic to fetch and display followers information
    return render_template('followers.html')
    
@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    try:
        data = request.get_json()

        post_id = data.get('post_id')
        comment_content = data.get('comment_content')

        if not post_id or not comment_content:
            return jsonify({'error': 'Post ID and comment content are required'}), 400

        new_comment = Comment(content=comment_content, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({'message': 'Comment added successfully'})
    except Exception as e:
        return jsonify({'error': f'Error adding comment: {str(e)}'})



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle user registration logic
        data = request.get_json()
        username = data['username']
        password = data['password']

        # checking if all info is filled
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400

        # checking if user is in the table
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username is already taken'}), 400

        # Create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Signup successful', 'user': {'username': new_user.username}}), 201

    # If it's a GET request, render the sign-up page
    return render_template('signup.html')


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
    

    
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))  # Redirect to the home page or another appropriate page

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    user_to_follow = User.query.get(user_id)
    
    if not user_to_follow:
        return jsonify({'error': 'User not found'}), 404

    if current_user.is_following(user_to_follow):
        return jsonify({'error': 'Already following this user'}), 400

    current_user.follow(user_to_follow)
    db.session.commit()
    
    return jsonify({'message': f'You are now following {user_to_follow.username}'})


@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    user_to_unfollow = User.query.get(user_id)

    if not user_to_unfollow:
        return jsonify({'error': 'User not found'}), 404

    if not current_user.is_following(user_to_unfollow):
        return jsonify({'error': 'You are not following this user'}), 400

    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    
    return jsonify({'message': f'You have unfollowed {user_to_unfollow.username}'})


@app.route('/get_followers', methods=['GET'])
@login_required
def get_followers():
    try:
        following = current_user.followed.all()
        followers = current_user.followers.all()

        following_data = [{'id': user.id, 'username': user.username} for user in following]
        followers_data = [{'id': user.id, 'username': user.username} for user in followers]

        return jsonify({'following': following_data, 'followers': followers_data})

    except Exception as e:
        return jsonify({'error': f'Error fetching followers: {str(e)}'}), 500


@app.route('/dashboardFeed', methods=['GET'])
@login_required
def dashboardFeed():
    try:
        # Retrieve all posts, not just those of the authenticated user
        posts = Post.query.all()

        # Convert posts to a format that can be easily serialized to JSON
        serialized_posts = [
            {
                'id': post.id,
                'content': post.content,
                'image': post.image,
                'date_posted': post.date_posted,
                'user': User.query.get(post.user_id).username,
                'comments': [{'content': comment.content, 'user': User.query.get(comment.user_id).username}
                             for comment in post.comments]
            }
            for post in posts
        ]

        return jsonify(serialized_posts)

    except Exception as e:
        return jsonify({'error': f'Error fetching posts: {str(e)}'}), 500


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Check if the current user is the owner of the post
    if current_user.id == post.user_id:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted successfully'})
    else:
        return jsonify({'error': 'You do not have permission to delete this post'}), 403


if __name__ == '__main__':
    app.run(debug=True)


