"""
Travel & Tourism Portal - Flask Application
Course: Web Technology (BIT233)
Complete Authentication System with Flask-Login, Flask-WTF, and Google OAuth
"""

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import os

# Import models and forms
from models import db, login_manager, User, Destination, Booking, Contact
from forms import RegistrationForm, LoginForm

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'travel_portal_secret_key_2024'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# WTForms configuration
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = 'travel_portal_csrf_secret_key_2024'

# Google OAuth Configuration
# Replace these with your actual credentials from Google Cloud Console
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET')

app.config['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET

# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with Flask-WTF form"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    # Display form errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{error}', 'danger')
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with Flask-WTF form"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            
            # Redirect to dashboard or next page
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    # Display form errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{error}', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# ==================== GOOGLE OAUTH ====================

@app.route('/login/google')
def google_login():
    """Initiate Google OAuth flow"""
    # Check if client ID is configured
    if GOOGLE_CLIENT_ID == 'YOUR_GOOGLE_CLIENT_ID' or GOOGLE_CLIENT_ID == '':
        flash('Google Sign-In requires OAuth credentials. See setup guide on login page.', 'warning')
        return redirect(url_for('login'))
    
    # Generate redirect URI
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/login/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get the authorization code from Google
        token = google.authorize_access_token()
        
        # Get user info from Google
        user_info = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        
        # Check if user already exists by Google ID
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if user exists by email (may have registered with email/password before)
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Link existing account with Google
                user.google_id = google_id
                db.session.commit()
                flash('Your account has been linked with Google.', 'success')
            else:
                # Create new user with Google info
                # Generate a unique username from Google name
                base_username = name.lower().replace(' ', '_') if name else email.split('@')[0]
                username = base_username
                counter = 1
                
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User(
                    username=username,
                    email=email,
                    google_id=google_id
                )
                # Google users don't have a password
                user.password_hash = None
                
                db.session.add(user)
                db.session.commit()
                flash('Account created successfully via Google!', 'success')
        
        # Log in the user
        login_user(user)
        flash('Logged in successfully with Google!', 'success')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash(f'Google login failed: {str(e)}', 'danger')
        return redirect(url_for('login'))


# ==================== ROUTES ====================

# Home Page
@app.route('/')
def index():
    # Use hardcoded destinations for homepage (mix of treks and cities)
    all_destinations = [
        # 4 Trekking destinations
        {
            'id': 1,
            'name': 'Everest Base Camp Trek',
            'location': 'Solukhumbu, Nepal',
            'description': 'Journey to the base of the world\'s highest peak.',
            'price': 2500,
            'package_type': 'Luxury',
            'image': 'https://images.unsplash.com/photo-1486911278844-a81c5267e227?w=800'
        },
        {
            'id': 2,
            'name': 'Annapurna Base Camp Trek',
            'location': 'Annapurna, Nepal',
            'description': 'Trek through diverse landscapes to the Annapurna massif.',
            'price': 1800,
            'package_type': 'Premium',
            'image': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800'
        },
        {
            'id': 3,
            'name': 'Langtang Valley Trek',
            'location': 'Langtang, Nepal',
            'description': 'Explore the Valley of Glaciers near Tibet.',
            'price': 1200,
            'package_type': 'Standard',
            'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800'
        },
        {
            'id': 5,
            'name': 'Mardi Himal Trek',
            'location': 'Annapurna, Nepal',
            'description': 'Breathtaking views of Mardi Peak and Annapurna range.',
            'price': 950,
            'package_type': 'Standard',
            'image': 'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=800'
        },
        # 2 City destinations
        {
            'id': 101,
            'name': 'Paris',
            'location': 'France',
            'description': 'Experience the City of Light and its iconic landmarks.',
            'price': 1299,
            'package_type': 'Premium',
            'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800'
        },
        {
            'id': 103,
            'name': 'Tokyo',
            'location': 'Japan',
            'description': 'Discover the blend of tradition and modernity.',
            'price': 1099,
            'package_type': 'Premium',
            'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800'
        }
    ]
    destinations = all_destinations
    return render_template('index.html', destinations=destinations)

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Destinations Page - Shows only category banners
@app.route('/destinations')
def destinations():
    """Destinations page showing only category banners"""
    categories = [
        {
            'id': 'treks',
            'name': 'Trekking in Nepal',
            'description': 'Embark on the adventure of a lifetime in the Himalayas',
            'image': 'https://images.unsplash.com/photo-1486911278844-a81c5267e227?w=1200',
            'icon': 'fa-mountain'
        },
        {
            'id': 'cities',
            'name': 'World Famous Cities',
            'description': 'Explore the world\'s most captivating destinations',
            'image': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200',
            'icon': 'fa-city'
        }
    ]
    return render_template('destinations.html', categories=categories)

# Packages Page
@app.route('/packages')
def packages():
    """Packages page with all trekking and city destinations"""
    package_type = request.args.get('type', 'all')
    
    # All packages data
    all_packages = [
        # Trekking packages (8)
        {
            'id': 1,
            'name': 'Everest Base Camp Trek',
            'category': 'trek',
            'location': 'Solukhumbu, Nepal',
            'description': 'Journey to the base of the world\'s highest peak.',
            'difficulty': 'Challenging',
            'duration': '14-16 days',
            'image': 'https://images.unsplash.com/photo-1486911278844-a81c5267e227?w=800',
            'price': 2500,
            'package_type': 'Luxury'
        },
        {
            'id': 2,
            'name': 'Annapurna Base Camp Trek',
            'category': 'trek',
            'location': 'Annapurna, Nepal',
            'description': 'Trek through diverse landscapes to the Annapurna massif.',
            'difficulty': 'Moderate',
            'duration': '10-12 days',
            'image': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800',
            'price': 1800,
            'package_type': 'Premium'
        },
        {
            'id': 3,
            'name': 'Langtang Valley Trek',
            'category': 'trek',
            'location': 'Langtang, Nepal',
            'description': 'Explore the Valley of Glaciers near Tibet.',
            'difficulty': 'Moderate',
            'duration': '8-10 days',
            'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
            'price': 1200,
            'package_type': 'Standard'
        },
        {
            'id': 4,
            'name': 'Manaslu Circuit Trek',
            'category': 'trek',
            'location': 'Gorkha, Nepal',
            'description': 'Circumnavigate the eighth highest mountain.',
            'difficulty': 'Challenging',
            'duration': '14-18 days',
            'image': 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=800',
            'price': 2200,
            'package_type': 'Premium'
        },
        {
            'id': 5,
            'name': 'Mardi Himal Trek',
            'category': 'trek',
            'location': 'Annapurna, Nepal',
            'description': 'Breathtaking views of Mardi Peak and Annapurna range.',
            'difficulty': 'Moderate',
            'duration': '6-8 days',
            'image': 'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=800',
            'price': 950,
            'package_type': 'Standard'
        },
        {
            'id': 6,
            'name': 'Gokyo Lakes Trek',
            'category': 'trek',
            'location': 'Solukhumbu, Nepal',
            'description': 'Discover sacred turquoise glacial lakes.',
            'difficulty': 'Moderate',
            'duration': '12-14 days',
            'image': 'https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=800',
            'price': 2100,
            'package_type': 'Premium'
        },
        {
            'id': 7,
            'name': 'Upper Mustang Trek',
            'category': 'trek',
            'location': 'Mustang, Nepal',
            'description': 'Journey to the forbidden kingdom.',
            'difficulty': 'Challenging',
            'duration': '15-18 days',
            'image': 'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800',
            'price': 3500,
            'package_type': 'Luxury'
        },
        {
            'id': 8,
            'name': 'Kanchenjunga Base Camp Trek',
            'category': 'trek',
            'location': 'Taplejung, Nepal',
            'description': 'Trek to the base of the third highest mountain.',
            'difficulty': 'Very Challenging',
            'duration': '18-22 days',
            'image': 'https://images.unsplash.com/photo-1434394354979-a235cd36269d?w=800',
            'price': 3200,
            'package_type': 'Luxury'
        },
        # City packages (8)
        {
            'id': 101,
            'name': 'Paris',
            'category': 'city',
            'location': 'France',
            'description': 'The City of Light with iconic landmarks.',
            'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800',
            'price': 1299,
            'package_type': 'Premium'
        },
        {
            'id': 102,
            'name': 'New York',
            'category': 'city',
            'location': 'USA',
            'description': 'The Big Apple with iconic skyline.',
            'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800',
            'price': 999,
            'package_type': 'Standard'
        },
        {
            'id': 103,
            'name': 'Tokyo',
            'category': 'city',
            'location': 'Japan',
            'description': 'Blend of ancient temples and technology.',
            'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800',
            'price': 1099,
            'package_type': 'Premium'
        },
        {
            'id': 104,
            'name': 'London',
            'category': 'city',
            'location': 'UK',
            'description': 'Royal palaces and historic landmarks.',
            'image': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800',
            'price': 1199,
            'package_type': 'Premium'
        },
        {
            'id': 105,
            'name': 'Sydney',
            'category': 'city',
            'location': 'Australia',
            'description': 'Stunning harbor and beautiful beaches.',
            'image': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800',
            'price': 1399,
            'package_type': 'Premium'
        },
        {
            'id': 106,
            'name': 'Rome',
            'category': 'city',
            'location': 'Italy',
            'description': 'The Eternal City with ancient ruins.',
            'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800',
            'price': 849,
            'package_type': 'Standard'
        },
        {
            'id': 107,
            'name': 'Dubai',
            'category': 'city',
            'location': 'UAE',
            'description': 'Futuristic skyscrapers and luxury.',
            'image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800',
            'price': 1599,
            'package_type': 'Luxury'
        },
        {
            'id': 108,
            'name': 'Cape Town',
            'category': 'city',
            'location': 'South Africa',
            'description': 'Stunning natural beauty with Table Mountain.',
            'image': 'https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800',
            'price': 1199,
            'package_type': 'Standard'
        }
    ]
    
    # Filter by package type
    if package_type == 'all':
        packages = all_packages
    else:
        packages = [p for p in all_packages if p['package_type'] == package_type]
    
    return render_template('packages.html', packages=packages, package_type=package_type)

# Mountain Treks Page
@app.route('/treks')
def treks():
    """Trekking destinations in Nepal"""
    treks = [
        {
            'id': 1,
            'name': 'Everest Base Camp Trek',
            'location': 'Solukhumbu, Nepal',
            'description': 'Journey to the base of the world\'s highest peak. Experience Sherpa culture, stunning mountain views, and the legendary Everest Base Camp.',
            'difficulty': 'Challenging',
            'duration': '14-16 days',
            'image': 'https://images.unsplash.com/photo-1486911278844-a81c5267e227?w=800',
            'price': 2500
        },
        {
            'id': 2,
            'name': 'Annapurna Base Camp Trek',
            'location': 'Annapurna, Nepal',
            'description': 'Trek through diverse landscapes to the heart of the Annapurna massif. Witness sunrise over the Himalayas from Poon Hill.',
            'difficulty': 'Moderate',
            'duration': '10-12 days',
            'image': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800',
            'price': 1800
        },
        {
            'id': 3,
            'name': 'Langtang Valley Trek',
            'location': 'Langtang, Nepal',
            'description': 'Explore the "Valley of Glaciers" near Tibet. Experience Tamang culture, rhododendron forests, and stunning alpine scenery.',
            'difficulty': 'Moderate',
            'duration': '8-10 days',
            'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
            'price': 1200
        },
        {
            'id': 4,
            'name': 'Manaslu Circuit Trek',
            'location': 'Gorkha, Nepal',
            'description': 'Circumnavigate the eighth highest mountain in the world. Experience remote villages, ancient monasteries, and dramatic landscapes.',
            'difficulty': 'Challenging',
            'duration': '14-18 days',
            'image': 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=800',
            'price': 2200
        },
        {
            'id': 5,
            'name': 'Mardi Himal Trek',
            'location': 'Annapurna, Nepal',
            'description': 'A hidden gem offering breathtaking views of Mardi Peak, Machapuchare, and the Annapurna range. Perfect for those seeking off-the-beaten-path adventures.',
            'difficulty': 'Moderate',
            'duration': '6-8 days',
            'image': 'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=800',
            'price': 950
        },
        {
            'id': 6,
            'name': 'Gokyo Lakes Trek',
            'location': 'Solukhumbu, Nepal',
            'description': 'Discover the sacred turquoise glacial lakes of Gokyo. Climb Gokyo Ri for panoramic views of Everest, Lhotse, and Makalu.',
            'difficulty': 'Moderate',
            'duration': '12-14 days',
            'image': 'https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=800',
            'price': 2100
        },
        {
            'id': 7,
            'name': 'Upper Mustang Trek',
            'location': 'Mustang, Nepal',
            'description': 'Journey to the forbidden kingdom with its Tibetan-influenced culture, ancient monasteries, and dramatic desert-like landscape.',
            'difficulty': 'Challenging',
            'duration': '15-18 days',
            'image': 'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800',
            'price': 3500
        },
        {
            'id': 8,
            'name': 'Kanchenjunga Base Camp Trek',
            'location': 'Taplejung, Nepal',
            'description': 'Trek to the base of the third highest mountain in the world. Experience pristine nature, rare wildlife, and remote villages.',
            'difficulty': 'Very Challenging',
            'duration': '18-22 days',
            'image': 'https://images.unsplash.com/photo-1434394354979-a235cd36269d?w=800',
            'price': 3200
        }
    ]
    return render_template('treks.html', treks=treks)

# World Cities Page
@app.route('/cities')
def cities():
    """World famous cities destinations"""
    cities = [
        {
            'id': 101,
            'name': 'Paris',
            'country': 'France',
            'description': 'The City of Light beckons with iconic landmarks like the Eiffel Tower, world-class museums, and exquisite French cuisine.',
            'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800',
            'price': 1299
        },
        {
            'id': 102,
            'name': 'New York',
            'country': 'USA',
            'description': 'The Big Apple offers iconic skyline, Broadway shows, diverse neighborhoods, and endless entertainment options.',
            'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800',
            'price': 999
        },
        {
            'id': 103,
            'name': 'Tokyo',
            'country': 'Japan',
            'description': 'A fascinating blend of ancient temples and cutting-edge technology. Experience sushi, shrines, and vibrant street life.',
            'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800',
            'price': 1099
        },
        {
            'id': 104,
            'name': 'London',
            'country': 'UK',
            'description': 'Royal palaces, historic pubs, and world-famous landmarks. Explore the British Museum and Buckingham Palace.',
            'image': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800',
            'price': 1199
        },
        {
            'id': 105,
            'name': 'Sydney',
            'country': 'Australia',
            'description': 'Stunning harbor views, beautiful beaches, and the iconic Opera House. Perfect for outdoor adventures.',
            'image': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800',
            'price': 1399
        },
        {
            'id': 106,
            'name': 'Rome',
            'country': 'Italy',
            'description': 'The Eternal City offers ancient ruins, Renaissance art, and delicious Italian cuisine. Walk through history.',
            'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800',
            'price': 849
        },
        {
            'id': 107,
            'name': 'Dubai',
            'country': 'UAE',
            'description': 'Futuristic skyscrapers, luxury shopping, and desert adventures. Experience opulence and innovation.',
            'image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800',
            'price': 1599
        },
        {
            'id': 108,
            'name': 'Cape Town',
            'country': 'South Africa',
            'description': 'Stunning natural beauty with Table Mountain, beautiful beaches, and wildlife. A vibrant multicultural city.',
            'image': 'https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800',
            'price': 1199
        }
    ]
    return render_template('cities.html', cities=cities)

# Contact Page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if name and email and message:
            contact = Contact(name=name, email=email, message=message)
            db.session.add(contact)
            db.session.commit()
            flash('Message sent successfully! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Please fill in all fields.', 'danger')
    
    return render_template('contact.html')

# Dashboard Page
@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    return render_template('dashboard.html', user=user, bookings=bookings)

# Admin Dashboard
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    destinations = Destination.query.all()
    return render_template('admin_dashboard.html', users=users, bookings=bookings, destinations=destinations)

# Booking Page
@app.route('/book/<int:destination_id>', methods=['GET', 'POST'])
@login_required
def book(destination_id):
    """Book a destination - always uses hardcoded destinations for treks and cities"""
    
    # Define valid destination IDs (treks: 1-8, cities: 101-108)
    trek_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    city_ids = [101, 102, 103, 104, 105, 106, 107, 108]
    
    # Trekking destinations (IDs 1-8)
    treks_data = {
        1: {'name': 'Everest Base Camp Trek', 'location': 'Solukhumbu, Nepal', 'price': 2500, 'image': 'https://images.unsplash.com/photo-1486911278844-a81c5267e227?w=800', 'package_type': 'Luxury'},
        2: {'name': 'Annapurna Base Camp Trek', 'location': 'Annapurna, Nepal', 'price': 1800, 'image': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800', 'package_type': 'Premium'},
        3: {'name': 'Langtang Valley Trek', 'location': 'Langtang, Nepal', 'price': 1200, 'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800', 'package_type': 'Standard'},
        4: {'name': 'Manaslu Circuit Trek', 'location': 'Gorkha, Nepal', 'price': 2200, 'image': 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=800', 'package_type': 'Premium'},
        5: {'name': 'Mardi Himal Trek', 'location': 'Annapurna, Nepal', 'price': 950, 'image': 'https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=800', 'package_type': 'Standard'},
        6: {'name': 'Gokyo Lakes Trek', 'location': 'Solukhumbu, Nepal', 'price': 2100, 'image': 'https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=800', 'package_type': 'Premium'},
        7: {'name': 'Upper Mustang Trek', 'location': 'Mustang, Nepal', 'price': 3500, 'image': 'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800', 'package_type': 'Luxury'},
        8: {'name': 'Kanchenjunga Base Camp Trek', 'location': 'Taplejung, Nepal', 'price': 3200, 'image': 'https://images.unsplash.com/photo-1434394354979-a235cd36269d?w=800', 'package_type': 'Luxury'}
    }
    
    # City destinations (IDs 101-108)
    cities_data = {
        101: {'name': 'Paris', 'country': 'France', 'price': 1299, 'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800', 'package_type': 'Premium'},
        102: {'name': 'New York', 'country': 'USA', 'price': 999, 'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800', 'package_type': 'Standard'},
        103: {'name': 'Tokyo', 'country': 'Japan', 'price': 1099, 'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800', 'package_type': 'Premium'},
        104: {'name': 'London', 'country': 'UK', 'price': 1199, 'image': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800', 'package_type': 'Premium'},
        105: {'name': 'Sydney', 'country': 'Australia', 'price': 1399, 'image': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800', 'package_type': 'Premium'},
        106: {'name': 'Rome', 'country': 'Italy', 'price': 849, 'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800', 'package_type': 'Standard'},
        107: {'name': 'Dubai', 'country': 'UAE', 'price': 1599, 'image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800', 'package_type': 'Luxury'},
        108: {'name': 'Cape Town', 'country': 'South Africa', 'price': 1199, 'image': 'https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800', 'package_type': 'Standard'}
    }
    
    # Check if destination is in hardcoded treks (priority)
    if destination_id in treks_data:
        data = treks_data[destination_id]
        destination = type('Destination', (), {
            'id': destination_id,
            'name': data['name'],
            'location': data['location'],
            'price': data['price'],
            'image': data['image'],
            'package_type': data['package_type'],
            'description': f'Book your {data["name"]} adventure with us. Experience the beauty of the Himalayas.'
        })()
    # Check if destination is in hardcoded cities (priority)
    elif destination_id in cities_data:
        data = cities_data[destination_id]
        destination = type('Destination', (), {
            'id': destination_id,
            'name': data['name'],
            'location': data['country'],
            'price': data['price'],
            'image': data['image'],
            'package_type': data['package_type'],
            'description': f'Book your trip to {data["name"]}, {data["country"]}. Experience the best of this amazing city.'
        })()
    # Check if destination is in database (fallback)
    else:
        destination = Destination.query.get(destination_id)
        if not destination:
            flash('Destination not found.', 'danger')
            return redirect(url_for('destinations'))
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        persons = request.form.get('persons')
        
        if not date_str or not persons:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('book', destination_id=destination_id))
        
        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            num_persons = int(persons)
            
            if num_persons < 1:
                flash('At least 1 person is required.', 'danger')
                return redirect(url_for('book', destination_id=destination_id))
            
            total_price = destination.price * num_persons
            
            # Determine category based on destination ID
            category = 'trek' if destination_id in treks_data else ('city' if destination_id in cities_data else 'other')
            
            # Get package_type from destination
            package_type = getattr(destination, 'package_type', 'Standard')
            
            # Always save booking to database with destination details
            booking = Booking(
                user_id=current_user.id,
                destination_id=destination_id,
                date=booking_date,
                persons=num_persons,
                total_price=total_price,
                status='Confirmed',
                destination_name=destination.name,
                destination_location=destination.location,
                destination_image=destination.image,
                destination_category=category,
                package_type=package_type
            )
            db.session.add(booking)
            db.session.commit()
            
            flash(f'Booking successful! Total price: ${total_price:.2f}', 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('book', destination_id=destination_id))
    
    return render_template('booking.html', destination=destination)

# Delete Booking
@app.route('/delete_booking/<int:booking_id>')
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to delete this booking.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

# Admin: Add Destination
@app.route('/add_destination', methods=['GET', 'POST'])
@login_required
def add_destination():
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        description = request.form.get('description')
        price = request.form.get('price')
        package_type = request.form.get('package_type')
        image = request.form.get('image')
        
        if name and location and description and price:
            destination = Destination(
                name=name,
                location=location,
                description=description,
                price=float(price),
                package_type=package_type,
                image=image if image else 'default.jpg'
            )
            db.session.add(destination)
            db.session.commit()
            flash('Destination added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Please fill in all required fields.', 'danger')
    
    return render_template('add_destination.html')

# Admin: Edit Destination
@app.route('/edit_destination/<int:destination_id>', methods=['GET', 'POST'])
@login_required
def edit_destination(destination_id):
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('login'))
    
    destination = Destination.query.get_or_404(destination_id)
    
    if request.method == 'POST':
        destination.name = request.form.get('name')
        destination.location = request.form.get('location')
        destination.description = request.form.get('description')
        destination.price = float(request.form.get('price'))
        destination.package_type = request.form.get('package_type')
        destination.image = request.form.get('image') or 'default.jpg'
        
        db.session.commit()
        flash('Destination updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_destination.html', destination=destination)

# Admin: Delete Destination
@app.route('/delete_destination/<int:destination_id>')
@login_required
def delete_destination(destination_id):
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('login'))
    
    destination = Destination.query.get_or_404(destination_id)
    
    # Delete related bookings first
    Booking.query.filter_by(destination_id=destination_id).delete()
    
    db.session.delete(destination)
    db.session.commit()
    flash('Destination and related bookings deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500


# ==================== DATABASE INITIALIZATION ====================

def init_database():
    """Initialize database and add sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@travelportal.com'
            )
            admin.set_password('admin123')
            admin.is_admin = True
            db.session.add(admin)
        
        # Add sample destinations if none exist
        if Destination.query.count() == 0:
            sample_destinations = [
                Destination(
                    name='Kathmandu Valley',
                    location='Kathmandu, Nepal',
                    description='Explore the ancient temples, rich culture, and vibrant markets of Nepal\'s capital city. Visit Swayambhunath, Pashupatinath, and the historic Durbar Square.',
                    price=450,
                    image='https://images.unsplash.com/photo-1574607383476-f2c71486e84b?w=800',
                    package_type='Standard'
                ),
                Destination(
                    name='Pokhara Lakeside',
                    location='Pokhara, Nepal',
                    description='Discover the stunning lakes, mountain views, and adventure activities in Pokhara. Visit Phewa Lake, Davis Falls, and enjoy paragliding.',
                    price=550,
                    image='https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=800',
                    package_type='Premium'
                ),
                Destination(
                    name='Chitwan Safari',
                    location='Chitwan, Nepal',
                    description='Experience the wildlife of Chitwan National Park with jungle safaris, elephant rides, and spotting rare one-horned rhinos and Bengal tigers.',
                    price=650,
                    image='https://images.unsplash.com/photo-1568322445389-f64ac2515020?w=800',
                    package_type='Premium'
                ),
                Destination(
                    name='Lumbini Pilgrimage',
                    location='Lumbini, Nepal',
                    description='Visit the birthplace of Lord Buddha, a UNESCO World Heritage Site. Explore ancient monasteries, the Maya Devi Temple, and the sacred garden.',
                    price=350,
                    image='https://images.unsplash.com/photo-1565966280129-5bf9f2849488?w=800',
                    package_type='Standard'
                ),
                Destination(
                    name='Nagarkot Sunrise',
                    location='Nagarkot, Nepal',
                    description='Witness breathtaking sunrise views over the Himalayas from Nagarkot hill station. Perfect for nature lovers and photography enthusiasts.',
                    price=280,
                    image='https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800',
                    package_type='Standard'
                ),
                Destination(
                    name='Bhaktapur Heritage',
                    location='Bhaktapur, Nepal',
                    description='Explore the well-preserved medieval city with its stunning architecture, pottery, and traditional Newari culture.',
                    price=320,
                    image='https://images.unsplash.com/photo-1599750691879-b592fa4f4bf3?w=800',
                    package_type='Standard'
                ),
                Destination(
                    name='Annapurna Trek',
                    location='Annapurna, Nepal',
                    description='Challenge yourself with one of the world\'s most famous trekking routes. Experience stunning mountain vistas and local Himalayan culture.',
                    price=1200,
                    image='https://images.unsplash.com/photo-1486911278844-a81c5267e227?w=800',
                    package_type='Luxury'
                ),
                Destination(
                    name='Mustang Desert',
                    location='Mustang, Nepal',
                    description='Journey to the forbidden kingdom of Mustang with its ancient monasteries, unique culture, and dramatic desert-like landscape.',
                    price=1500,
                    image='https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
                    package_type='Luxury'
                )
            ]
            db.session.add_all(sample_destinations)
        
        db.session.commit()
        print("Database initialized successfully!")
        print("Admin login: admin@travelportal.com / admin123")
        print("\n" + "="*60)
        print("GOOGLE OAUTH SETUP INSTRUCTIONS:")
        print("="*60)
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Go to APIs & Services > Credentials")
        print("4. Create OAuth 2.0 Client ID")
        print("5. Set authorized redirect URI to:")
        print("   http://127.0.0.1:5000/login/google/callback")
        print("6. Copy CLIENT_ID and CLIENT_SECRET")
        print("7. Set environment variables:")
        print("   set GOOGLE_CLIENT_ID=your_client_id")
        print("   set GOOGLE_CLIENT_SECRET=your_client_secret")
        print("="*60)


# ==================== MAIN ====================

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
