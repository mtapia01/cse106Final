from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session,send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import os

UPLOAD_FOLDER = 'uploads'


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
app.config['SECRET_KEY'] = 'key' 
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    likes = db.Column(db.Integer, nullable=False, default=0)  # Default 0

    def __repr__(self):
        return f"Post('{self.content}', '{self.date_posted}')"

    def save_picture(self, picture):
        # Save the picture to the server's static folder
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture.filename)
        picture.save(picture_path)

        # Set the image field in the Post model to the filename
        self.image = picture.filename
    
    comments = db.relationship('Comment', backref='post', lazy=True)

class Follower(db.Model):
    followee_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    def __repr__(self):
        return f"Followers('{self.followee_id}', '{self.follower_id}')"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

#is_authenticated
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True, default='ValleHS-06.jpg')

    def get_id(self):
        return str(self.id) 
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

# Used to link pictures to site
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

            flash("Post created successfully", "success")
            
            return redirect(url_for('feed'))
            #jsonify({'message': 'Post created successfully'})
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

@app.route('/get_followers', methods=['GET'])
@login_required
def get_followers():
    try:
        user_id = current_user.id

        # Assuming you have a User model with a 'followed' relationship
        user = User.query.filter_by(id=user_id).first()

        following = user.followed.all()
        followers = user.followers.all()

        following_data = [{'id': u.id, 'username': u.username} for u in following]
        followers_data = [{'id': u.id, 'username': u.username} for u in followers]

        return jsonify({'following': following_data, 'followers': followers_data})

    except Exception as e:
        return jsonify({'error': f'Error fetching followers data: {str(e)}'}), 500
    
    
@app.route('/profile')
def profile():
    # You can add logic here to fetch user information from the database
    # and pass it to the template if needed.
    return render_template('profile.html')  # Assuming your profile HTML file is named 'profile.html'

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

    data = request.get_json()
    username = data['username']
    password = data['password']

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400


    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Login successful
        login_user(user) 
        return jsonify({'message': 'Login successful', 'user': {'username': user.username}})
    else:
        # Invalid username or password
        return jsonify({'error': 'Invalid username or password'}), 401
    

    
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index')) 

@app.route('/followUser', methods=['POST'])
@login_required
def follow_user():
    try:
        data = request.get_json()
        if current_user.is_authenticated:
            follower_id = current_user.id

        followee_id = data.get('followee')

        # Check if the user is already following the followee
        if not Follower.query.filter_by(followee_id=followee_id, follower_id=follower_id).first():

            followers_relation = Follower(followee_id=followee_id, follower_id=follower_id)
            db.session.add(followers_relation)

            db.session.commit()

            return jsonify({'message': 'User followed successfully'})
        else:
            return jsonify({'message': 'You are already following this user'})

    except Exception as e:
        return jsonify({'error': f'Error following user: {str(e)}'})
    
@app.route('/unfollow', methods=['POST'])
@login_required
def unfollow_user():
    try:
        data = request.get_json()
        if current_user.is_authenticated:
            follower_id = current_user.id

        followee_id = data.get('followee')

        # Check if the user is already following the followee
        if Follower.query.filter_by(followee_id=followee_id, follower_id=follower_id).first():
            followers_relation = Follower.query.filter_by(followee_id=followee_id, follower_id=follower_id).first()
            db.session.delete(followers_relation)

            # Commit the changes
            db.session.commit()

            return jsonify({'message': 'User unfollowed successfully'})
        else:
            return jsonify({'message': 'You don\'t follow this user... yet'})

    except Exception as e:
        return jsonify({'error': f'Error unfollowing user: {str(e)}'})

@app.route('/explorFeed', methods=['GET'])
@login_required
def explorFeed():
    try:
        posts = Post.query.all()

        # Convert posts to JSON
        serialized_posts = [
            {
                'id': post.id,
                'user_id': post.user_id,
                'likes': post.likes if hasattr(post, 'likes') else 0, 
                'content': post.content,
                'image': post.image,
                'date_posted': post.date_posted,
                'user': User.query.get(post.user_id).username,
                'comments': [{'content': comment.content, 'user': User.query.get(comment.user_id).username}
                             for comment in post.comments],
            }
            for post in posts
        ]

        return jsonify(serialized_posts)

    except Exception as e:
        return jsonify({'error': f'Error fetching posts: {str(e)}'}), 500


@app.route('/userFeed', methods=['GET'])
@login_required
def userFeed():
    try:
        # Retrieve posts from users that the current user is following using the Followers table
        following_posts = (
            Post.query.join(User, User.id == Post.user_id)
            .join(Follower, Follower.followee_id == User.id)
            .filter(Follower.follower_id == current_user.id)
            .all()
        )

        # Convert posts JSON
        serialized_posts = [
            {
                'id': post.id,
                'user_id': post.user_id,
                'likes': post.likes if hasattr(post, 'likes') else 0,
                'content': post.content,
                'image': post.image,
                'date_posted': post.date_posted,
                'user': User.query.get(post.user_id).username,
                'comments': [{'content': comment.content, 'user': User.query.get(comment.user_id).username}
                             for comment in post.comments],
            }
            for post in following_posts
        ]

        return jsonify(serialized_posts)

    except Exception as e:
        return jsonify({'error': f'Error fetching posts: {str(e)}'}), 500
    
@app.route('/like', methods=['POST'])
@login_required
def like_post():
    try:
        data = request.get_json()
        post_id = data.get('postId')
        user_id = current_user.id

        post = Post.query.get(post_id)
        post.likes += 1

        db.session.commit()

        return jsonify({'message': 'Post liked successfully', 'likes': post.likes})
    except Exception as e:
        return jsonify({'error': f'Error liking post: {str(e)}'})

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


