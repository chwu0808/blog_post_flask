from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class Registration():
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired(), Length(min = 6, max = 30)])
    confirm_pwd = PasswordField('Confirm Password', validators = [DataRequired(), Length(min = 6, max = 30), EqualTo(password)])

    submit = SubmitField('Sign Up')

class Login():
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired(), Length(min = 6, max = 30)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')



@app.route('/register')
def register():
    r_form = Registration()
    return render_template('register.html', form = r_form)

@app.route('/login')
def login():
    login_form = Login()
    return render_template('login.html', form = login_form)
