#!/usr/bin/env python
"""
WSN Intrusion Detection System - Setup and Initialization Script
Run this script to set up the application
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print_success("Python version is compatible")
        return True
    else:
        print_error("Python 3.8 or higher is required")
        return False

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = [
        'templates',
        'templates/errors',
        'static',
        'models',
        'uploads'
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created {directory}/")
        else:
            print(f"Directory already exists: {directory}/")

def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print_success("All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies")
        return False

def setup_database():
    """Initialize database"""
    print_header("Setting Up Database")
    
    try:
        from app import app, init_db
        
        with app.app_context():
            print("Initializing database...")
            init_db()
            print_success("Database initialized successfully")
            
            # Create demo user
            from app import User, db
            
            demo_user = User.query.filter_by(username='demo').first()
            if not demo_user:
                print("Creating demo user...")
                demo_user = User(
                    username='demo',
                    email='demo@wsn-ids.com',
                    full_name='Demo User'
                )
                demo_user.set_password('demo123')
                db.session.add(demo_user)
                db.session.commit()
                print_success("Demo user created (username: demo, password: demo123)")
            else:
                print("Demo user already exists")
        
        return True
    except Exception as e:
        print_error(f"Database setup failed: {str(e)}")
        return False

def check_dataset():
    """Check if dataset exists"""
    print_header("Dataset Check")
    
    if Path("WSN-DS.csv").exists():
        print_success("Dataset found: WSN-DS.csv")
        return True
    else:
        print_warning("Dataset not found: WSN-DS.csv")
        print("Please ensure WSN-DS.csv is in the project root directory")
        print("You can train models after adding the dataset")
        return False

def check_models():
    """Check if ML models exist"""
    print_header("ML Models Check")
    
    required_models = [
        'decision_tree_model.pkl',
        'scaler.pkl',
        'label_encoder.pkl'
    ]
    
    all_exist = True
    for model in required_models:
        if Path(model).exists():
            print_success(f"Found: {model}")
        else:
            print_warning(f"Not found: {model}")
            all_exist = False
    
    if not all_exist:
        print("\nYou can train models by running: python backend.py")
        print("(Requires WSN-DS.csv in the project root)")
    
    return all_exist

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_header("Environment Configuration")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    elif env_example.exists():
        # Copy example to .env
        import shutil
        shutil.copy(env_example, env_file)
        print_success(".env file created from .env.example")
        print_warning("Please update SECRET_KEY in .env for production")
        return True
    else:
        print_warning(".env file not created")
        print("Create .env file with configuration if needed")
        return False

def print_next_steps():
    """Print next steps"""
    print_header("Setup Complete!")
    
    print("""
Next Steps:

1. PREPARE DATASET (Optional)
   - Place your WSN-DS.csv in the project root
   - Then run: python backend.py

2. RUN APPLICATION
   - Start the server: python app.py
   - Open browser: http://localhost:5000

3. LOGIN
   - Username: demo
   - Password: demo123
   - Or create your own account

4. MAKE PREDICTIONS
   - Navigate to Prediction page
   - Enter network features
   - Click "Analyze Network & Predict"

5. VIEW ANALYTICS
   - Check visualizations page
   - View model performance metrics

DOCUMENTATION:
   - README.md - Full documentation
   - .env.example - Configuration template

TROUBLESHOOTING:
   - Check wsn_app.log for application errors
   - Check model_training.log for training errors
   - Ensure Python 3.8+ is installed

Questions? Check README.md for detailed instructions.
    """)

def main():
    """Main setup function"""
    print("\n")
    print("╔═════════════════════════════════════════════════════════╗")
    print("║   WSN Intrusion Detection System - Setup Script         ║")
    print("║   Professional Edition v2.0.0                           ║")
    print("╚═════════════════════════════════════════════════════════╝")
    
    steps = [
        ("Checking Python Version", check_python_version),
        ("Creating Directories", create_directories),
        ("Installing Dependencies", install_dependencies),
        ("Creating Environment File", create_env_file),
        ("Setting Up Database", setup_database),
        ("Checking Dataset", check_dataset),
        ("Checking ML Models", check_models),
    ]
    
    completed = 0
    for step_name, step_func in steps:
        try:
            if step_func():
                completed += 1
        except Exception as e:
            print_error(f"{step_name} failed: {str(e)}")
    
    print("\n" + "="*60)
    print(f"Setup Progress: {completed}/{len(steps)} steps completed")
    print("="*60)
    
    if completed == len(steps):
        print_next_steps()
        print_success("Setup completed successfully!")
        return 0
    else:
        print_warning(f"Setup completed with {len(steps) - completed} warnings")
        print("\nReview the messages above and resolve any issues.")
        return 1

if __name__ == '__main__':
    exit(main())
