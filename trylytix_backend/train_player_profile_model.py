# Run this once to generate the model
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# 1. Sample dataset — You can build this from actual DB later
data = [
    # tackles, missed, passes, carries, runs, label
    [12, 2, 8, 5, 2, 'Defender'],
    [2, 0, 25, 2, 1, 'Playmaker'],
    [6, 1, 12, 9, 3, 'Attacker'],
    [1, 0, 20, 1, 0, 'Playmaker'],
    [10, 4, 7, 3, 2, 'Defender'],
    [4, 1, 15, 5, 4, 'Attacker'],
]

df = pd.DataFrame(data, columns=[
    'tackles', 'missed_tackles', 'passes', 'carries', 'runs', 'label'
])

X = df.drop('label', axis=1)
y = df['label']

# Normalize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

# Save model and scaler
joblib.dump(model, 'player_profile_rf_model.pkl')
joblib.dump(scaler, 'player_profile_scaler.pkl')

print("✅ Model and scaler saved.")
