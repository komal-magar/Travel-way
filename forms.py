"""
WTForms for Travel & Tourism Portal
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User


class RegistrationForm(FlaskForm):
    """Registration form with validation"""
    username = StringField('Username', 
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=25, message='Username must be between 3 and 25 characters')
        ],
        render_kw={'placeholder': 'Choose a username'}
    )
    email = StringField('Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address')
        ],
        render_kw={'placeholder': 'Enter your email'}
    )
    password = PasswordField('Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=6, message='Password must be at least 6 characters')
        ],
        render_kw={'placeholder': 'Create a password'}
    )
    confirm_password = PasswordField('Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm your password'}
    )
    submit = SubmitField('Create Account')
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class LoginForm(FlaskForm):
    """Login form with validation"""
    email = StringField('Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address')
        ],
        render_kw={'placeholder': 'Enter your email'}
    )
    password = PasswordField('Password',
        validators=[
            DataRequired(message='Password is required')
        ],
        render_kw={'placeholder': 'Enter your password'}
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    def validate_email(self, email):
        """Check if email exists"""
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('No account found with this email. Please register first.')
    
    def validate_password(self, password):
        """This is called after other validations pass"""
        pass


class LoginWithGoogleForm(FlaskForm):
    """Dummy form for Google OAuth (just for CSRF protection)"""
    submit = SubmitField('Continue with Google')
