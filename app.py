#import package
from flask import Flask, render_template, url_for, redirect, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

#initialize the flask app
app = Flask(__name__)

#config
app.config['SECRET_KEY'] = 'c3f5063bce66fdc92a470b52850097dc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

#set database, hash passward, login_manager
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#login_manager load
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#User info database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True, nullable = False)
    username = db.Column(db.String(30), unique = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)
    image = db.Column(db.String(120), nullable = False, default = 'default.jpg')
    posts = db.relationship('Post', backref = 'author', lazy = True)

    def __repr__(self):
        return "User('{self.email}', '{self.username}', '{self.image}')"

#blog post info database
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    date_post = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)

    def __repr__(self):
        return "Post('{self.title}', '{self.date_post}')"

#home page
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

#register page
@app.route('/register', methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        user_email = request.form.get('Email')
        user_username = request.form.get('username')
        user_password = request.form.get('Password')
        user_confirm = request.form.get('confirm')
        hash_password = bcrypt.generate_password_hash(user_password).decode('utf-8')
        if user_password == user_confirm:
            new_user = User(email = user_email, username = user_username, password = hash_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect (url_for('login'))
        else:
            flash("Password does not match, please try again!", "danger")
            return render_template('register.html')
    return render_template('register.html')

#login page
@app.route('/login', methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        user_email = request.form.get('Email')
        user_password = request.form.get('Password')

        user = User.query.filter_by(email = user_email).first()
        if user:
            if bcrypt.check_password_hash(user.password, user_password):
                login_user(user, remember = request.form.get('remember'))
                next_page = request.args.get('next')
                flash("You're now login.", "success")
                return redirect (next_page) if next_page else redirect (url_for('home'))
            else:
                flash("Incorrect password, please try again", "danger")
                return render_template('login.html')
        else:
            flash("User not found.", "danger")
            return render_template('login.html')
    return render_template('login.html')

#logout page
@app.route('/logout')
def logout():
    logout_user()
    flash("You're now logout.", "warning")
    return redirect (url_for('home'))

#user account info page
@app.route('/account')
@login_required
def account():
    return render_template('account.html')

#blog posts display page
@app.route('/posts')
def posts():
    all_posts = Post.query.order_by(Post.date_post).all()
    return render_template('post.html', posts = all_posts)

#create a new post page
@app.route('/posts/create', methods = ["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        post_title = request.form.get('Title')
        post_content = request.form.get('Content')

        new_post = Post(title = post_title, content = post_content, author = current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect (url_for('posts'))
    return render_template('create.html')

#single blog post info page
@app.route('/posts/<int:post_id>')
def blog(post_id):
    blog = Post.query.get_or_404(post_id)
    return render_template('blog.html', post = blog)

#edit a post page 
@app.route('/posts/<int:post_id>/edit/', methods = ["GET", "POST"])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if request.method == "POST":
        post.title = request.form.get('Title')
        post.content = request.form.get('Content')
        post.date_post = datetime.utcnow()
        db.session.commit()
        flash("Your post has been updated!", "success")
        return redirect (url_for('posts'))
    else:
        return render_template('edit.html', post = post)

#delete a post page
@app.route('/posts/<int:post_id>/delete', methods = ["POST"])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", "warning")
    return redirect (url_for('posts'))

if __name__ == '__main__': 
    app.run(debug = True)