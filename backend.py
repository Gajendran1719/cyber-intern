"""
WSN Intrusion Detection System - Model Training Pipeline
Trains Decision Tree, ANN, and CNN models with proper evaluation
"""

import pandas as pd
import numpy as np
import os
import pickle
import logging
from datetime import datetime

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

import matplotlib.pyplot as plt
import seaborn as sns

# =====================
# SETUP LOGGING
# =====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =====================
# CONFIGURATION
# =====================

class Config:
    """Configuration for model training"""
    DATASET_PATH = "WSN-DS.csv"  # Update path as needed
    MODELS_DIR = "models"
    RESULTS_DIR = "static"
    RANDOM_STATE = 42
    TEST_SIZE = 0.20
    
    # Model hyperparameters
    DT_MAX_DEPTH = 15
    DT_MIN_SAMPLES_SPLIT = 10
    
    ANN_EPOCHS = 50
    ANN_BATCH_SIZE = 32
    
    CNN_EPOCHS = 50
    CNN_BATCH_SIZE = 32

# Create necessary directories
os.makedirs(Config.MODELS_DIR, exist_ok=True)
os.makedirs(Config.RESULTS_DIR, exist_ok=True)

# =====================
# DATA LOADING & PREPROCESSING
# =====================

def load_and_preprocess_data(filepath):
    """Load and preprocess WSN dataset"""
    logger.info(f"Loading dataset from {filepath}")
    
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Dataset shape: {df.shape}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle missing values
        missing_values = df.isnull().sum()
        if missing_values.any():
            logger.warning(f"Missing values found:\n{missing_values[missing_values > 0]}")
            df = df.dropna()
        
        # Display class distribution
        target_column = "Attack type"
        logger.info(f"\nClass Distribution:")
        logger.info(df[target_column].value_counts())
        
        return df
    
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise

def encode_features(X, le_dict=None):
    """Encode categorical features"""
    X_encoded = X.copy()
    
    if le_dict is None:
        le_dict = {}
    
    for col in X_encoded.columns:
        if X_encoded[col].dtype == "object":
            if col not in le_dict:
                le_dict[col] = LabelEncoder()
                X_encoded[col] = le_dict[col].fit_transform(X_encoded[col].astype(str))
            else:
                X_encoded[col] = le_dict[col].transform(X_encoded[col].astype(str))
    
    return X_encoded, le_dict

# =====================
# MODEL TRAINING - DECISION TREE
# =====================

def train_decision_tree(X_train, X_test, y_train, y_test):
    """Train Decision Tree Classifier"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING DECISION TREE")
    logger.info("="*50)
    
    try:
        dt = DecisionTreeClassifier(
            max_depth=Config.DT_MAX_DEPTH,
            min_samples_split=Config.DT_MIN_SAMPLES_SPLIT,
            random_state=Config.RANDOM_STATE
        )
        
        dt.fit(X_train, y_train)
        
        # Predictions
        dt_pred = dt.predict(X_test)
        
        # Metrics
        dt_acc = accuracy_score(y_test, dt_pred)
        dt_prec = precision_score(y_test, dt_pred, average='weighted', zero_division=0)
        dt_recall = recall_score(y_test, dt_pred, average='weighted', zero_division=0)
        dt_f1 = f1_score(y_test, dt_pred, average='weighted', zero_division=0)
        
        # Cross-validation
        cv_scores = cross_val_score(dt, X_train, y_train, cv=5)
        
        logger.info(f"Accuracy:  {dt_acc*100:.2f}%")
        logger.info(f"Precision: {dt_prec*100:.2f}%")
        logger.info(f"Recall:    {dt_recall*100:.2f}%")
        logger.info(f"F1-Score:  {dt_f1*100:.2f}%")
        logger.info(f"CV Mean:   {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
        
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, dt_pred))
        
        return dt, dt_pred, {
            'accuracy': dt_acc,
            'precision': dt_prec,
            'recall': dt_recall,
            'f1_score': dt_f1,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    except Exception as e:
        logger.error(f"Error training Decision Tree: {str(e)}")
        raise

# =====================
# MODEL TRAINING - ANN
# =====================

def train_ann(X_train, X_test, y_train, y_test, num_classes):
    """Train Artificial Neural Network"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING ARTIFICIAL NEURAL NETWORK (ANN)")
    logger.info("="*50)
    
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, Dropout
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.callbacks import EarlyStopping
        
        ann = Sequential([
            Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.1),
            Dense(num_classes, activation='softmax')
        ])
        
        ann.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Early stopping
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
        
        # Train
        history = ann.fit(
            X_train, y_train,
            epochs=Config.ANN_EPOCHS,
            batch_size=Config.ANN_BATCH_SIZE,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Predictions
        ann_pred_prob = ann.predict(X_test, verbose=0)
        ann_pred = np.argmax(ann_pred_prob, axis=1)
        
        # Metrics
        ann_acc = accuracy_score(y_test, ann_pred)
        ann_prec = precision_score(y_test, ann_pred, average='weighted', zero_division=0)
        ann_recall = recall_score(y_test, ann_pred, average='weighted', zero_division=0)
        ann_f1 = f1_score(y_test, ann_pred, average='weighted', zero_division=0)
        
        logger.info(f"Accuracy:  {ann_acc*100:.2f}%")
        logger.info(f"Precision: {ann_prec*100:.2f}%")
        logger.info(f"Recall:    {ann_recall*100:.2f}%")
        logger.info(f"F1-Score:  {ann_f1*100:.2f}%")
        
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, ann_pred))
        
        return ann, ann_pred, {
            'accuracy': ann_acc,
            'precision': ann_prec,
            'recall': ann_recall,
            'f1_score': ann_f1
        }
    
    except Exception as e:
        logger.error(f"Error training ANN: {str(e)}")
        raise

# =====================
# MODEL TRAINING - CNN
# =====================

def train_cnn(X_train, X_test, y_train, y_test, num_classes):
    """Train Convolutional Neural Network"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING CONVOLUTIONAL NEURAL NETWORK (CNN)")
    logger.info("="*50)
    
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.callbacks import EarlyStopping
        
        # Reshape for CNN
        X_train_cnn = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test_cnn = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
        
        cnn = Sequential([
            Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=(X_train_cnn.shape[1], 1)),
            MaxPooling1D(pool_size=2),
            Conv1D(filters=64, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            Flatten(),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(num_classes, activation='softmax')
        ])
        
        cnn.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Early stopping
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
        
        # Train
        history = cnn.fit(
            X_train_cnn, y_train,
            epochs=Config.CNN_EPOCHS,
            batch_size=Config.CNN_BATCH_SIZE,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Predictions
        cnn_pred_prob = cnn.predict(X_test_cnn, verbose=0)
        cnn_pred = np.argmax(cnn_pred_prob, axis=1)
        
        # Metrics
        cnn_acc = accuracy_score(y_test, cnn_pred)
        cnn_prec = precision_score(y_test, cnn_pred, average='weighted', zero_division=0)
        cnn_recall = recall_score(y_test, cnn_pred, average='weighted', zero_division=0)
        cnn_f1 = f1_score(y_test, cnn_pred, average='weighted', zero_division=0)
        
        logger.info(f"Accuracy:  {cnn_acc*100:.2f}%")
        logger.info(f"Precision: {cnn_prec*100:.2f}%")
        logger.info(f"Recall:    {cnn_recall*100:.2f}%")
        logger.info(f"F1-Score:  {cnn_f1*100:.2f}%")
        
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, cnn_pred))
        
        return cnn, cnn_pred, {
            'accuracy': cnn_acc,
            'precision': cnn_prec,
            'recall': cnn_recall,
            'f1_score': cnn_f1
        }
    
    except Exception as e:
        logger.error(f"Error training CNN: {str(e)}")
        raise

# =====================
# VISUALIZATION
# =====================

def plot_confusion_matrix(y_true, y_pred, title, filename):
    """Plot and save confusion matrix"""
    try:
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Predicted', fontsize=12)
        plt.ylabel('Actual', fontsize=12)
        plt.tight_layout()
        
        filepath = os.path.join(Config.RESULTS_DIR, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        logger.info(f"Saved {filename}")
    except Exception as e:
        logger.error(f"Error plotting confusion matrix: {str(e)}")

def plot_accuracy_comparison(results):
    """Plot accuracy comparison"""
    try:
        models = list(results.keys())
        accuracies = [results[m]['accuracy']*100 for m in models]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(models, accuracies, color=['#2ecc71', '#3498db', '#e74c3c'])
        
        for i, (bar, acc) in enumerate(zip(bars, accuracies)):
            plt.text(bar.get_x() + bar.get_width()/2, acc + 1, f'{acc:.2f}%',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.title('Model Accuracy Comparison', fontsize=16, fontweight='bold')
        plt.xlabel('Models', fontsize=12)
        plt.ylabel('Accuracy (%)', fontsize=12)
        plt.ylim(0, 105)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        filepath = os.path.join(Config.RESULTS_DIR, 'accuracy_comparison.png')
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        logger.info("Saved accuracy_comparison.png")
    except Exception as e:
        logger.error(f"Error plotting accuracy: {str(e)}")

# =====================
# SAVE MODELS
# =====================

def save_models(dt_model, scaler, label_encoder, ann_model=None, cnn_model=None):
    """Save trained models"""
    try:
        # Save Decision Tree
        with open('decision_tree_model.pkl', 'wb') as f:
            pickle.dump(dt_model, f)
        logger.info("Saved decision_tree_model.pkl")
        
        # Save Scaler
        with open('scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        logger.info("Saved scaler.pkl")
        
        # Save Label Encoder
        with open('label_encoder.pkl', 'wb') as f:
            pickle.dump(label_encoder, f)
        logger.info("Saved label_encoder.pkl")
        
        # Save ANN
        if ann_model:
            ann_model.save('ann_model.h5')
            logger.info("Saved ann_model.h5")
        
        # Save CNN
        if cnn_model:
            cnn_model.save('cnn_model.h5')
            logger.info("Saved cnn_model.h5")
    
    except Exception as e:
        logger.error(f"Error saving models: {str(e)}")
        raise

# =====================
# MAIN PIPELINE
# =====================

def main():
    """Main training pipeline"""
    logger.info("\n" + "="*70)
    logger.info("WSN INTRUSION DETECTION - MODEL TRAINING PIPELINE")
    logger.info("="*70)
    
    try:
        # Load and preprocess data
        df = load_and_preprocess_data(Config.DATASET_PATH)
        
        # Prepare features and target
        target_column = "Attack type"
        X = df.drop(target_column, axis=1)
        y = df[target_column]
        
        # Encode target variable
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        num_classes = len(label_encoder.classes_)
        
        logger.info(f"\nNumber of classes: {num_classes}")
        logger.info(f"Classes: {label_encoder.classes_}")
        
        # Encode features
        X_encoded, le_dict = encode_features(X)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_encoded)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded,
            test_size=Config.TEST_SIZE,
            random_state=Config.RANDOM_STATE,
            stratify=y_encoded
        )
        
        logger.info(f"\nTraining set size: {X_train.shape[0]}")
        logger.info(f"Test set size: {X_test.shape[0]}")
        logger.info(f"Number of features: {X_train.shape[1]}")
        
        # Train models
        results = {}
        
        dt_model, dt_pred, dt_metrics = train_decision_tree(X_train, X_test, y_train, y_test)
        results['Decision Tree'] = dt_metrics
        
        ann_model, ann_pred, ann_metrics = train_ann(X_train, X_test, y_train, y_test, num_classes)
        results['ANN'] = ann_metrics
        
        cnn_model, cnn_pred, cnn_metrics = train_cnn(X_train, X_test, y_train, y_test, num_classes)
        results['CNN'] = cnn_metrics
        
        # Final comparison
        logger.info("\n" + "="*50)
        logger.info("FINAL RESULTS COMPARISON")
        logger.info("="*50)
        
        for model, metrics in results.items():
            logger.info(f"\n{model}:")
            logger.info(f"  Accuracy:  {metrics['accuracy']*100:.2f}%")
            logger.info(f"  Precision: {metrics['precision']*100:.2f}%")
            logger.info(f"  Recall:    {metrics['recall']*100:.2f}%")
            logger.info(f"  F1-Score:  {metrics['f1_score']*100:.2f}%")
        
        # Save models
        save_models(dt_model, scaler, label_encoder, ann_model, cnn_model)
        
        # Generate visualizations
        logger.info("\nGenerating visualizations...")
        plot_confusion_matrix(y_test, dt_pred, 'Decision Tree Confusion Matrix', 'dt_confusion.png')
        plot_confusion_matrix(y_test, ann_pred, 'ANN Confusion Matrix', 'ann_confusion.png')
        plot_confusion_matrix(y_test, cnn_pred, 'CNN Confusion Matrix', 'cnn_confusion.png')
        plot_accuracy_comparison(results)
        
        logger.info("\n" + "="*70)
        logger.info("TRAINING COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        
        return True
    
    except Exception as e:
        logger.error(f"\nTraining pipeline failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
