from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length



# Registration
class RegisterForm(FlaskForm):
    firstname = StringField('firstname', validators=[InputRequired(),
                Length(min=2, max=50)], render_kw={"placeholder":"Firstname"})
    lastname = StringField('lastname', validators=[InputRequired(),
                Length(min=2, max=50)], render_kw={"placeholder":"Lastname"})
    company = StringField('company', validators=[InputRequired(),
                Length(min=3, max=50)], render_kw={"placeholder":"Company"})
    country = StringField('country', validators=[InputRequired(),
                Length(min=3, max=50)], render_kw={"placeholder":"Country"})
    email = StringField("Email", validators=[InputRequired(), Email(message="Invalid Email"), 
                Length(max=50)], render_kw={"placeholder": "Email Address"})
    password = PasswordField('Password', validators=[InputRequired(), 
                Length(min=8, max=80)], render_kw={"placeholder":"Password"})

    submit = SubmitField("Register")


# Login
class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Length(min=6, max=50)],
                render_kw={"placeholder":"Email"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)],
                render_kw={"placeholder":"Password"})

    remember = BooleanField('remember')

    submit = SubmitField("Login")
