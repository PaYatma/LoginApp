from flask import Blueprint
from myforms import RegisterForm
from models import User
from extensions import db
from flask_mail import Mail, Message
from flask import redirect, url_for, flash, render_template
from itsdangerous import SignatureExpired, URLSafeTimedSerializer

sendmail = Blueprint('sendmail', __name__)

mail = Mail(sendmail)

sendmail.config.from_pyfile('config.cfg')



# Function for sending email 
def gettoken(email):

    s = URLSafeTimedSerializer(sendmail.secret_key)
    token = s.dumps(email, salt=sendmail.config['SECURITY_PASSWORD_SALT'])
    msg = Message('Confirm Email', sender='noreply.ysr@gmail.com', recipients=[email])   
    link = url_for('confirm_link', token=token, _external=True)
    msg.body = '''Please, click on this link to confirm your email: {}.
    After 1 hour, this link will not be valid anymore.'''.format(link)
    mail.send(msg)

    return token


# Function to confirm email address
@sendmail.route("/confirm/<token>", methods=['GET', 'POST'])
def confirm_link(token):
    form = RegisterForm()
    s = URLSafeTimedSerializer(sendmail.secret_key)
    try:
        email=s.loads(token, salt=sendmail.config['SECURITY_PASSWORD_SALT'], max_age=3600*24*360) 
        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
            user_exist.confirm_email = True
            db.session.commit()
    except SignatureExpired:      
        return render_template('expired.html')

    return redirect(url_for('welcome'))
