"""
Train TF-IDF + Logistic Regression content classifier.
Run after generate_training_data.py
"""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

DATA_PATH  = os.path.join(os.path.dirname(__file__), '../data/content_training_data.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/content_classifier.pkl')

print("Loading training data...")
df = pd.read_csv(DATA_PATH)
print(f"Total samples: {len(df)}")
print(f"Label distribution:\n{df['label'].value_counts()}\n")

X, y = df['text'], df['label']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=15000,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
        strip_accents='unicode',
    )),
    ('clf', LogisticRegression(
        C=1.0,
        max_iter=1000,
        class_weight='balanced',
        random_state=42,
    ))
])

print("Training content classifier...")
pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Test Accuracy: {acc:.4f} ({acc*100:.1f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)
print(f"\n✅ Model saved to: {MODEL_PATH}")
