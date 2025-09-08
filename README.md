# Kidney Disease Detection using Decision Tree

## Overview
This project uses a **Decision Tree classifier** to detect **kidney disease** based on patient medical records.  
The model classifies whether a patient is at risk or not.

## Features
- Input: Patient health features (blood pressure, glucose, creatinine, etc.)  
- Output: Classification – `Chronic Kidney Disease` or `No Disease`  
- Simple and interpretable decision rules  

## Steps
1. **Data Collection**: Gather dataset from medical records or open datasets (e.g., UCI Kidney Disease Dataset)  
2. **Preprocessing**: Handle missing values, normalize/encode data if needed  
3. **Model Training**: Train a Decision Tree classifier  
4. **Prediction & Evaluation**: Predict kidney disease risk and evaluate accuracy, precision, recall  

## Python Example

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Load dataset
data = pd.read_csv("kidney_disease.csv")

# Features and target
X = data.drop('target', axis=1)  # target = 'ckd' column
y = data['target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Decision Tree
dtree = DecisionTreeClassifier(criterion='entropy', max_depth=5, random_state=42)
dtree.fit(X_train, y_train)

# Predictions
y_pred = dtree.predict(X_test)

# Evaluate
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
