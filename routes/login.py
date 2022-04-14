from flask import Blueprint
from ..myforms import LoginForm
from ..models import User
from ..extensions import db
from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_login import login_user
from flask import redirect, url_for, flash, session, request, render_template
from flask_login import login_user, LoginManager

login = Blueprint('sign', __name__)

bcrypt = Bcrypt(login)


# Login settings
login_manager = LoginManager()
login_manager.init_app(login)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Login
@login.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    session.permanent = True        
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
    
        if user:
            if not user.confirm_email:
                flash('Please, confirm your email. And try again.', category='warning')
                redirect(url_for('login'))
            elif user.confirm_email and bcrypt.check_password_hash(user.password, form.password.data):
                isremember = True if request.form.get('remember') else False
                print(isremember)
                if isremember:
                    login_user(user, remember=isremember, duration=timedelta(seconds=30), fresh=True)
                else:
                    login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('This password is invalid. Please, try again.', category='error')
                redirect(url_for('login'))
        else:
            flash('Email address unknown. Correct the email address. Or create an account.', category='warning')  

    return render_template('login.html', form=form)
    
