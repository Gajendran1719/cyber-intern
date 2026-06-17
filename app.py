"""
WSN Intrusion Detection System - Enhanced Flask Application
Professional version with database integration and security
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import pickle
import numpy as np
import logging
import os
from functools import wraps

# Configuration
class Config:
    """Application configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///wsn_detection.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wsn_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# =====================
# DATABASE MODELS
# =====================

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Prediction(db.Model):
    """Model to store user predictions"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Input features
    features = db.Column(db.JSON, nullable=False)
    
    # Prediction results
    dt_prediction = db.Column(db.String(100))  # Decision Tree
    ann_prediction = db.Column(db.String(100))  # ANN
    cnn_prediction = db.Column(db.String(100))  # CNN
    final_prediction = db.Column(db.String(100), nullable=False)
    
    # Confidence scores
    dt_confidence = db.Column(db.Float)
    ann_confidence = db.Column(db.Float)
    cnn_confidence = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Prediction {self.id} - {self.final_prediction}>'


# =====================
# LOAD ML MODELS
# =====================

def load_models():
    """Load pre-trained ML models"""
    try:
        model_files = {
            'dt_model': 'decision_tree_model.pkl',
            'scaler': 'scaler.pkl',
            'label_encoder': 'label_encoder.pkl'
        }
        
        models = {}
        for key, filename in model_files.items():
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    models[key] = pickle.load(f)
                logger.info(f"Loaded {key} from {filename}")
            else:
                logger.warning(f"Model file {filename} not found")
        
        return models
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return {}

# Global model storage
ML_MODELS = load_models()

# =====================
# LOGIN MANAGER
# =====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================
# UTILITY FUNCTIONS
# =====================

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format"""
    if len(username) < 3 or len(username) > 20:
        return False
    if not username.isalnum() and '_' not in username:
        return False
    return True

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, "Valid"

# =====================
# ROUTES - AUTHENTICATION
# =====================

@app.route('/')
def index():
    """Home page - redirect based on auth status"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            full_name = request.form.get('full_name', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            if not username or not email or not full_name or not password:
                flash('All fields are required!', 'danger')
                return redirect(url_for('register'))
            
            if not validate_username(username):
                flash('Username must be 3-20 characters (alphanumeric and underscore only)', 'danger')
                return redirect(url_for('register'))
            
            if not validate_email(email):
                flash('Invalid email format!', 'danger')
                return redirect(url_for('register'))
            
            is_valid, msg = validate_password(password)
            if not is_valid:
                flash(msg, 'danger')
                return redirect(url_for('register'))
            
            if password != confirm_password:
                flash('Passwords do not match!', 'danger')
                return redirect(url_for('register'))
            
            if len(full_name) < 2:
                flash('Full name must be at least 2 characters!', 'danger')
                return redirect(url_for('register'))
            
            # Check if user exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists!', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered!', 'danger')
                return redirect(url_for('register'))
            
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=full_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {username}")
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Username and password are required!', 'danger')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password) and user.is_active:
                login_user(user, remember=request.form.get('remember_me'))
                logger.info(f"User logged in: {username}")
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                logger.warning(f"Failed login attempt for: {username}")
                flash('Invalid username or password!', 'danger')
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# =====================
# ROUTES - MAIN PAGES
# =====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    try:
        user_predictions = Prediction.query.filter_by(user_id=current_user.id)\
            .order_by(Prediction.created_at.desc()).limit(5).all()
        total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
        
        return render_template(
            'dashboard.html',
            user=current_user,
            recent_predictions=user_predictions,
            total_predictions=total_predictions
        )
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard', 'danger')
        return redirect(url_for('login'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Prediction page"""
    if request.method == 'POST':
        return redirect(url_for('run_prediction'))
    
    # Feature names for reference
    features = [
        ('f1', 'ID'),
        ('f2', 'Time'),
        ('f3', 'Is_CH'),
        ('f4', 'Who_CH'),
        ('f5', 'Dist_To_CH'),
        ('f6', 'ADV_S'),
        ('f7', 'ADV_R'),
        ('f8', 'JOIN_S'),
        ('f9', 'JOIN_R'),
        ('f10', 'SCH_S'),
        ('f11', 'SCH_R'),
        ('f12', 'Rank'),
        ('f13', 'DATA_S'),
        ('f14', 'DATA_R'),
        ('f15', 'Data_Sent_To_BS'),
        ('f16', 'Dist_CH_To_BS'),
        ('f17', 'Send_Code'),
        ('f18', 'Expanded_Energy')
    ]
    
    return render_template('predict.html', features=features)

@app.route('/prediction', methods=['POST'])
@login_required
def run_prediction():
    """Run prediction with ML models"""
    try:
        if not ML_MODELS or 'dt_model' not in ML_MODELS:
            flash('ML models not loaded. Please contact administrator.', 'danger')
            logger.error("ML models not available for prediction")
            return redirect(url_for('predict'))
        
        # Collect features
        features = []
        feature_names = []
        
        for i in range(1, 19):
            try:
                value = float(request.form.get(f'f{i}'))
                features.append(value)
                feature_names.append(f'f{i}')
            except (TypeError, ValueError):
                flash(f'Invalid value for feature {i}. Please enter a valid number.', 'danger')
                logger.warning(f"Invalid input for feature f{i}")
                return redirect(url_for('predict'))
        
        # Prepare data
        data = np.array([features])
        
        # Scale data
        scaled_data = ML_MODELS['scaler'].transform(data)
        
        # Make predictions
        dt_pred = ML_MODELS['dt_model'].predict(scaled_data)
        dt_attack = ML_MODELS['label_encoder'].inverse_transform(dt_pred)[0]
        
        # Store prediction in database
        prediction = Prediction(
            user_id=current_user.id,
            features=dict(zip(feature_names, features)),
            dt_prediction=str(dt_attack),
            final_prediction=str(dt_attack)
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        logger.info(f"Prediction made by {current_user.username}: {dt_attack}")
        
        return render_template(
            'predict.html',
            prediction=dt_attack,
            features=[(f'f{i}', f'Feature {i}') for i in range(1, 19)]
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        flash(f'Error during prediction: {str(e)}', 'danger')
        return redirect(url_for('predict'))

@app.route('/visualization')
@login_required
def visualization():
    """Visualization page"""
    try:
        # Check if visualization images exist
        static_dir = 'static'
        images = {
            'accuracy': os.path.exists(os.path.join(static_dir, 'accuracy.png')),
            'dt_confusion': os.path.exists(os.path.join(static_dir, 'dt_confusion.png')),
            'ann_confusion': os.path.exists(os.path.join(static_dir, 'ann_confusion.png')),
            'cnn_confusion': os.path.exists(os.path.join(static_dir, 'cnn_confusion.png'))
        }
        
        return render_template('visualization.html', images=images)
    except Exception as e:
        logger.error(f"Visualization error: {str(e)}")
        flash('Error loading visualizations', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/history')
@login_required
def history():
    """Prediction history"""
    try:
        page = request.args.get('page', 1, type=int)
        predictions = Prediction.query.filter_by(user_id=current_user.id)\
            .order_by(Prediction.created_at.desc())\
            .paginate(page=page, per_page=10)
        
        return render_template('history.html', predictions=predictions)
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        flash('Error loading history', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        
        if not full_name or not email:
            flash('All fields are required!', 'danger')
            return redirect(url_for('profile'))
        
        if not validate_email(email):
            flash('Invalid email format!', 'danger')
            return redirect(url_for('profile'))
        
        # Check if email is already used by another user
        existing_email = User.query.filter_by(email=email).filter(User.id != current_user.id).first()
        if existing_email:
            flash('Email already in use!', 'danger')
            return redirect(url_for('profile'))
        
        current_user.full_name = full_name
        current_user.email = email
        current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Profile updated for user: {current_user.username}")
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error: {str(e)}")
        flash('Error updating profile', 'danger')
        return redirect(url_for('profile'))

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_user.check_password(old_password):
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('profile'))
        
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            flash(msg, 'danger')
            return redirect(url_for('profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match!', 'danger')
            return redirect(url_for('profile'))
        
        current_user.set_password(new_password)
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Password changed for user: {current_user.username}")
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error: {str(e)}")
        flash('Error changing password', 'danger')
        return redirect(url_for('profile'))

# =====================
# ERROR HANDLERS
# =====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 Error: {request.url}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    logger.error(f"500 Error: {str(error)}")
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    logger.warning(f"403 Forbidden: {request.url}")
    return render_template('errors/403.html'), 403

# =====================
# CONTEXT PROCESSORS
# =====================

@app.context_processor
def inject_user():
    """Make current_user available in all templates"""
    return dict(current_user=current_user)

# =====================
# DATABASE INITIALIZATION
# =====================

def init_db():
    """Initialize database"""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")

# =====================
# MAIN
# =====================

if __name__ == '__main__':
    init_db()
    logger.info("Starting WSN Intrusion Detection System")
    app.run(
        debug=True,
        use_reloader=False,
        host='0.0.0.0',
        port=5000
    )
