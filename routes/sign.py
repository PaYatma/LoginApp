from flask import Blueprint
from myforms import RegisterForm
from models import User
from extensions import db
from flask_bcrypt import Bcrypt
from sendmail import gettoken
from flask import redirect, url_for, flash, render_template

signup = Blueprint('sign', __name__)

bcrypt = Bcrypt(signup)


# Sign-up
@signup.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        company=form.company.data,
                        country=form.country.data,
                        email=form.email.data, 
                        password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            gettoken(email=form.email.data)

        except:
            flash("This email address already exists. Please, login from here.", category='info')
            return redirect(url_for('login')) 

        return redirect(url_for('login')) 

    return render_template('register.html', form=form)

