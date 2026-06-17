# WSN IDS - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Setup Script
```bash
python setup.py
```

### 3. Start Application
```bash
python app.py
```

### 4. Access Application
Open browser: `http://localhost:5000`

### 5. Login
- **Username**: demo
- **Password**: demo123

---

## 📊 Train ML Models (Optional)

```bash
# 1. Add your WSN-DS.csv to project root
# 2. Run training script
python backend.py
# 3. Models will be generated in ~5-10 minutes
```

---

## 🎯 Key Features Walkthrough

### Dashboard
- View statistics and recent predictions
- Quick access to all features

### Make Predictions
1. Click "Prediction" in navbar
2. Enter 18 network features
3. Click "Analyze Network & Predict"
4. View result immediately

### View Analytics
- See model accuracy comparison
- Explore confusion matrices
- Compare Decision Tree, ANN, CNN

### Prediction History
- View all your past predictions
- Click "Details" to see input features
- Paginated view (10 per page)

### Profile
- Update full name and email
- Change password securely
- View account statistics

---

## 📁 Important Files

```
app.py                 Main application with database models
backend.py            Model training pipeline
requirements.txt      Python dependencies
setup.py              Automated setup script
README.md             Complete documentation
.env.example          Configuration template
```

```
templates/            HTML pages (Jinja2)
static/               Generated charts and images
wsn_detection.db      SQLite database (auto-created)
```

---

## 🔧 Configuration

### Change Port
Edit `app.py`:
```python
app.run(host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Change Database
Edit `app.py`:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/wsn_db'
```

### Change Secret Key (IMPORTANT!)
Create `.env`:
```
SECRET_KEY=your-very-secret-key-minimum-32-chars
```

---

## 📝 Features Summary

✅ **Authentication**
- Secure registration & login
- Password hashing with salt
- Session management

✅ **Machine Learning**
- Decision Tree (fast, interpretable)
- ANN (accurate, deep learning)
- CNN (powerful, sequential analysis)
- Model evaluation & metrics

✅ **Database**
- User management
- Prediction history
- Persistent storage

✅ **UI/UX**
- Professional Bootstrap 5 design
- Responsive mobile layouts
- Interactive dashboards
- Real-time alerts

✅ **Analytics**
- Accuracy comparison charts
- Confusion matrices
- Performance metrics
- Prediction tracking

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(port=5001)
```

### Models Not Loaded
```bash
python backend.py  # Train models first
```

### Database Locked
```bash
rm wsn_detection.db  # Delete and recreate
python app.py       # Restart
```

### Module Not Found
```bash
pip install -r requirements.txt  # Reinstall dependencies
```

---

## 🔐 Security Notes

1. **Change SECRET_KEY** before production
2. **Update database** to PostgreSQL for production
3. **Enable HTTPS** and set `SESSION_COOKIE_SECURE = True`
4. **Use strong passwords** (minimum 6 characters recommended)
5. **Regularly backup** database

---

## 📞 Support

Check these files for help:
- **README.md** - Complete documentation
- **wsn_app.log** - Application errors
- **model_training.log** - Training errors

---

## ✨ Next Steps

1. ✓ Install & run application
2. ✓ Create user account
3. ✓ Make a test prediction
4. ✓ View analytics
5. ✓ Train your own models with dataset
6. ✓ Deploy to production

---

**Version**: 2.0.0 Professional Edition  
**Status**: Production Ready ✓  
**Last Updated**: 2024
