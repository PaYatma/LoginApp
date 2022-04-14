from flask import redirect, Blueprint, render_template, url_for
from flask_login import login_user, login_required
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import User
from .myforms import RegisterForm, LoginForm

auth = Blueprint('auth', __name__)
signup_print = Blueprint('signup_print', __name__)
login_print = Blueprint('login_print', __name__)
logout_print = Blueprint('logout_print', __name__)
dash_print = Blueprint('dash_print', __name__)



@auth.route("/")
def welcome():
    return "<h1> Welcome to the app!!! </h1>"


# routes
@auth.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")


@login_print.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid email or password</h1>'

    return render_template('login.html', form=form)



@signup_print.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        country=form.country.data,
                        email=form.email.data, 
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login')) #'<h1>New user has been created!</h1>'

    return render_template('register.html', form=form)

@logout_print.route('/logout')
def logout():
    return render_template('logout.html')