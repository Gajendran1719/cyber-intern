# WSN Intrusion Detection System (Professional Edition)

A complete, production-ready Wireless Sensor Network Intrusion Detection System with database integration, secure authentication, and advanced machine learning models.

## 🎯 Features

### ✅ Authentication & Security
- **Secure User Registration & Login** with password hashing (werkzeug.security)
- **Session Management** with Flask-Login
- **Input Validation** and sanitization
- **CSRF Protection** (Flask default)
- **Password Strength Requirements** (minimum 6 characters)
- **Email Validation**

### 📊 Machine Learning
- **Decision Tree Classifier** - Fast and interpretable
- **Artificial Neural Network (ANN)** - Deep learning accuracy
- **Convolutional Neural Network (CNN)** - Sequential data analysis
- **Model Evaluation** with confusion matrices and accuracy metrics
- **Feature Scaling** with StandardScaler
- **Cross-Validation** for robust evaluation

### 💾 Database
- **SQLite Database** with SQLAlchemy ORM
- **User Management** - Secure user storage
- **Prediction History** - Track all user predictions
- **Data Persistence** - Automatic migration support

### 🎨 Professional UI/UX
- **Bootstrap 5** responsive design
- **Modern Gradient Styling** with custom CSS
- **Interactive Dashboards** with statistics
- **Data Visualization** (confusion matrices, accuracy charts)
- **Mobile-Friendly** layouts
- **Alert System** with auto-dismiss notifications

### 📈 Analytics & Reporting
- **Prediction History** with pagination
- **Model Comparison** statistics
- **Performance Metrics** visualization
- **User Activity Tracking**

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone or Setup Project
```bash
# Navigate to project directory
cd wsn-intrusion-detection

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Prepare Dataset
```bash
# Place your WSN dataset (WSN-DS.csv) in the project root directory
# Update the dataset path in backend.py if needed:
# DATASET_PATH = "path/to/your/WSN-DS.csv"
```

### Step 4: Train ML Models
```bash
# Run the training script to generate models
python backend.py

# This will create:
# - decision_tree_model.pkl
# - scaler.pkl
# - label_encoder.pkl
# - ann_model.h5
# - cnn_model.h5
# - Visualization images in static/
```

### Step 5: Initialize Database
```bash
# Database will auto-initialize on first run
# Or manually initialize with Python:
python
>>> from app import app, init_db
>>> init_db()
>>> exit()
```

### Step 6: Run Application
```bash
python app.py

# Application will be available at:
# http://localhost:5000
```

## 📝 Usage Guide

### First Time Setup
1. **Navigate to Login Page** → Click "Register"
2. **Fill Registration Form**:
   - Full Name (2+ characters)
   - Email (valid email format)
   - Username (3-20 alphanumeric + underscore)
   - Password (minimum 6 characters)
3. **Create Account** and you're ready to go!

### Making Predictions
1. **Navigate to Prediction Page** from dashboard
2. **Enter Network Features** (18 input fields):
   - ID, Time, Is_CH, Who_CH, Dist_To_CH
   - ADV_S, ADV_R, JOIN_S, JOIN_R
   - SCH_S, SCH_R, Rank
   - DATA_S, DATA_R, Data_Sent_To_BS
   - Dist_CH_To_BS, Send_Code, Expanded_Energy
3. **Click "Analyze Network & Predict"**
4. **View Result** - Attack type detected by Decision Tree model
5. **Track History** - Automatic saving in prediction history

### Viewing Analytics
1. **Navigate to Visualizations Page**
2. **View Model Comparison** - Accuracy chart for all 3 models
3. **Explore Confusion Matrices** - Detailed performance analysis
4. **Compare Models** - Decision Tree, ANN, CNN side-by-side

### Managing Profile
1. **Click Username** in navbar → Profile
2. **Update Information** - Full name, email
3. **Change Password** - Old and new password
4. **View Statistics** - Account creation date, status

## 📁 Project Structure

```
wsn-intrusion-detection/
│
├── app.py                      # Main Flask application
├── backend.py                  # Model training pipeline
├── requirements.txt            # Python dependencies
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navbar
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # User dashboard
│   ├── predict.html           # Prediction form
│   ├── visualization.html     # Analytics dashboard
│   ├── history.html           # Prediction history
│   ├── profile.html           # User profile
│   └── errors/                # Error pages
│       ├── 404.html
│       ├── 500.html
│       └── 403.html
│
├── static/                     # Static files
│   ├── accuracy_comparison.png
│   ├── dt_confusion.png
│   ├── ann_confusion.png
│   └── cnn_confusion.png
│
├── models/                     # ML models (after training)
│   ├── decision_tree_model.pkl
│   ├── scaler.pkl
│   └── label_encoder.pkl
│
├── wsn_detection.db           # SQLite database (auto-created)
├── wsn_app.log                # Application logs
└── model_training.log         # Training logs
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in project root:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-in-production
DEBUG=False

# Database
DATABASE_URL=sqlite:///wsn_detection.db

# Security
SESSION_COOKIE_SECURE=True  # Set to True for HTTPS
```

### Application Configuration
Edit `Config` class in `app.py`:

```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///wsn_detection.db'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    SESSION_COOKIE_SECURE = False  # Change to True for production
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
```

## 🧠 Machine Learning Models

### Decision Tree Classifier
- **Type**: Classical Machine Learning
- **Speed**: Very Fast ⚡
- **Interpretability**: High ✓
- **Use Case**: Real-time predictions
- **Hyperparameters**:
  - max_depth: 15
  - min_samples_split: 10

### Artificial Neural Network (ANN)
- **Type**: Deep Learning
- **Architecture**: 128 → 64 → 32 → output
- **Speed**: Medium
- **Accuracy**: Excellent
- **Use Case**: Complex pattern recognition
- **Features**: Dropout layers, early stopping

### Convolutional Neural Network (CNN)
- **Type**: Deep Learning
- **Architecture**: Conv1D → MaxPooling → Dense layers
- **Speed**: Medium
- **Accuracy**: Excellent
- **Use Case**: Sequential data analysis
- **Features**: Conv layers for feature extraction

## 📊 Database Schema

### Users Table
```
id (Primary Key)
username (Unique)
email (Unique)
full_name
password_hash
created_at
updated_at
is_active
```

### Predictions Table
```
id (Primary Key)
user_id (Foreign Key)
features (JSON)
dt_prediction
ann_prediction
cnn_prediction
final_prediction
dt_confidence
ann_confidence
cnn_confidence
created_at
```

## 🔐 Security Features

1. **Password Hashing**: Werkzeug PBKDF2 with salt
2. **SQL Injection Prevention**: SQLAlchemy parameterized queries
3. **XSS Protection**: Jinja2 auto-escaping
4. **CSRF Protection**: Flask default CSRF handling
5. **Session Security**: HTTPOnly cookies, SameSite policy
6. **Input Validation**: Type checking and length validation
7. **Error Handling**: Generic error messages to users

## 📝 API Endpoints

| Route | Method | Auth | Purpose |
|-------|--------|------|---------|
| `/` | GET | - | Redirect to login/dashboard |
| `/register` | GET, POST | - | User registration |
| `/login` | GET, POST | - | User login |
| `/logout` | GET | ✓ | User logout |
| `/dashboard` | GET | ✓ | Main dashboard |
| `/predict` | GET, POST | ✓ | Prediction form |
| `/prediction` | POST | ✓ | Run prediction |
| `/visualization` | GET | ✓ | Analytics page |
| `/history` | GET | ✓ | Prediction history |
| `/profile` | GET | ✓ | User profile |
| `/profile/update` | POST | ✓ | Update profile |
| `/profile/change-password` | POST | ✓ | Change password |

## 🧪 Testing

### Test with Demo Account
- **Username**: demo
- **Password**: demo123

(Create a demo user via registration page)

### Test Predictions
Use sample network data from your WSN dataset to test predictions.

## 📊 Performance Metrics

### Expected Accuracies (on test set)
- **Decision Tree**: 85-92%
- **ANN**: 90-95%
- **CNN**: 88-94%

(Depends on dataset quality and size)

## 🔍 Troubleshooting

### Issue: Models not loaded
```
Solution: Run backend.py to train and generate models
```

### Issue: Database locked
```
Solution: Delete wsn_detection.db and restart application
```

### Issue: Port 5000 already in use
```
Solution: Change port in app.py:
app.run(host='0.0.0.0', port=5001)
```

### Issue: TensorFlow not installing
```
Solution: Install CPU version:
pip install tensorflow-cpu
```

## 📚 Dependencies

- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-Login** - Session management
- **Werkzeug** - Security utilities
- **scikit-learn** - ML algorithms
- **TensorFlow/Keras** - Deep learning
- **NumPy/Pandas** - Data processing
- **Matplotlib/Seaborn** - Visualization

## 🚀 Deployment

### Production Checklist
- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG = False
- [ ] Use HTTPS (SESSION_COOKIE_SECURE = True)
- [ ] Use production database (PostgreSQL recommended)
- [ ] Set up logging and monitoring
- [ ] Configure CORS if needed
- [ ] Use WSGI server (Gunicorn, uWSGI)
- [ ] Set up reverse proxy (Nginx)

### Deploy with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📞 Support & Contribution

For issues, improvements, or contributions:
1. Report bugs with clear description
2. Suggest features with use cases
3. Submit pull requests with documentation

## 📄 License

This project is provided for educational and professional use.

## 🎓 Author Notes

This enhanced version includes:
- Professional database integration with SQLAlchemy
- Secure authentication with password hashing
- Complete prediction history tracking
- Beautiful responsive UI with Bootstrap 5
- Comprehensive error handling and logging
- Production-ready code structure
- Complete documentation and setup guide

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✓
