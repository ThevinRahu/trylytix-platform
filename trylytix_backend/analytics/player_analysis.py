import os
import pandas as pd
import numpy as np
import joblib
from events.models import Event

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'player_profile_rf_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '..', 'player_profile_scaler.pkl')
LE_PATH = os.path.join(os.path.dirname(__file__), '..', 'player_profile_label_encoder.pkl')

EVENT_TO_FEATURE = {
    'rucks_won': 'rucks_won',
    'run': 'runs',
    'tackle': 'tackles',
    'free_kick_conceded': 'total_free_kicks_conceded',
    'lineout': 'total_lineouts',
    'try': 'tries',
    'try_assist': 'try_assists',
    'turnover_knock_on': 'turnover_knock_on',
    'turnover_conceded': 'turnovers_conceded',
    'yellow_card': 'yellow_cards',
}

def fetch_player_events(player_id):
    # You may want to join with other tables to get more event types/fields if available
    events = Event.objects.filter(player_id=player_id).values('event_type')
    return pd.DataFrame(list(events))

def extract_feature_vector(events_df):
    counts = events_df['event_type'].value_counts().to_dict()
    # Create feature vector using all expected fields; default to 0
    features = {model_field: 0 for model_field in EVENT_TO_FEATURE.values()}
    for event_type, model_field in EVENT_TO_FEATURE.items():
        features[model_field] = counts.get(event_type, 0)
    return features

def deep_rf_analysis(player_id):
    if not (os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH) and os.path.exists(LE_PATH)):
        return {"error": "ML model or scaler/label encoder not found. Train it first."}

    df = fetch_player_events(player_id)
    if df.empty:
        return {"error": "No data for player"}

    features = extract_feature_vector(df)
    X = pd.DataFrame([features])

    # Load model, scaler, and label encoder
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    le = joblib.load(LE_PATH)

    X_scaled = scaler.transform(X)
    pred_idx = model.predict(X_scaled)[0]
    prediction = le.inverse_transform([pred_idx])[0]
    prob = model.predict_proba(X_scaled)[0]

    confidence = dict(
        zip(le.inverse_transform(np.arange(len(prob))), [f"{p*100:.1f}%" for p in prob])
    )

    return {
        "player_id": player_id,
        "predicted_profile": prediction,
        "confidence_scores": confidence,
        "raw_metrics": features,
        "insights": generate_insights(features, prediction)
    }

def generate_insights(features, label):
    """
    Generates insights using both the descriptive label and the raw feature values.
    You can expand this logic to be more sophisticated using thresholds, feature importances, etc.
    """
    insights = [f"Profile summary: {label}"]

    # Example: auto-highlight key stats
    if features.get("tackles", 0) > 100:
        insights.append("Outstanding defensive workload (high tackles).")
    if features.get("rucks_won", 0) > 50:
        insights.append("Dominant at the breakdown (high rucks won).")
    if features.get("tries", 0) > 10:
        insights.append("Major attacking threat (high try count).")
    if features.get("yellow_cards", 0) > 0:
        insights.append("Disciplinary issues detected (yellow cards).")
    if features.get("turnover_knock_on", 0) > 20:
        insights.append("Needs work on handling (many knock-ons).")
    if features.get("turnovers_conceded", 0) > 20:
        insights.append("High turnover rate.")

    # Fallback for balanced player
    if len(insights) == 1:
        insights.append("Balanced statistical profile.")

    return insights