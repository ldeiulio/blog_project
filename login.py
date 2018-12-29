from flask_login import LoginManager, logout_user, login_user, login_required
from flask import request, render_template, flash, redirect, abort
from urllib.parse import urlparse, urljoin
from .database import app, db_session, User

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "/login"
login_manager.login_message_category = "danger"


# renders login.html for login, on POST checks if email and password combo exists as record in User
# if record does not exist, flashes message and redisplay page
# if record does exist, logs in user and redirects with GET argument 'next' if argument is safe, else redirects to index
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == "POST":
        email = request.form['email']
        query = db_session.query(User).filter_by(email=email).first()
        if query is None or query.password != request.form['password']:
            flash("incorrect email or password")
        else:
            login_user(query)
            next_url = request.args.get('next')
            if not is_safe_url(next_url):
                return abort(400)
            return redirect(next_url or '/')
    return render_template("login.html")


# determines if target is a safe url to redirect to
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# if username is not already used and if passwords match, creates new User as per form specification
# does not currently check if email is valid
# redirects to index
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == "POST":
        server_email = db_session.query(User.email).filter_by(email=request.form['email']).first()
        if server_email is not None:
            flash("email already registered")
            return render_template("register.html")
        if request.form['password'] != request.form['confirm_password']:
            flash("passwords do not match")
            return render_template("register.html")
        user = User(name=request.form['name'], email=request.form['email'], password=request.form['password'])
        db_session.add(user)
        db_session.commit()
        login_user(user)
        flash("registered")
        return redirect('/')
    return render_template("register.html")


# logs out user, redirects to index
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# requirement function for flask-login
@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))
