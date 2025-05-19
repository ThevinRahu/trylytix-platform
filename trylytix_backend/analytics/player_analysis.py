import os
import pandas as pd
import numpy as np
import joblib
from events.models import Event

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'player_profile_rf_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '..', 'player_profile_scaler.pkl')


def fetch_player_events(player_id):
    events = Event.objects.filter(player_id=player_id).values('event_type')
    return pd.DataFrame(list(events))


def extract_feature_vector(events_df):
    counts = events_df['event_type'].value_counts().to_dict()

    tackles = counts.get('tackle', 0)
    missed = counts.get('missed_tackle', 0)
    passes = counts.get('pass', 0)
    carries = counts.get('carry', 0)
    runs = counts.get('run', 0)

    return {
        'tackles': tackles,
        'missed_tackles': missed,
        'passes': passes,
        'carries': carries,
        'runs': runs
    }


def deep_rf_analysis(player_id):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        return {"error": "ML model not found. Train it first."}

    df = fetch_player_events(player_id)
    if df.empty:
        return {"error": "No data for player"}

    features = extract_feature_vector(df)
    X = pd.DataFrame([features])

    # Load model and scaler
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    X_scaled = scaler.transform(X)
    prediction = model.predict(X_scaled)[0]
    prob = model.predict_proba(X_scaled)[0]

    # Detailed confidence
    confidence = dict(zip(model.classes_, [f"{p*100:.1f}%" for p in prob]))

    return {
        "player_id": player_id,
        "predicted_profile": prediction,
        "confidence_scores": confidence,
        "raw_metrics": features,
        "insights": generate_insights(features, prediction)
    }


def generate_insights(features, label):
    insights = []

    if label == "Defender":
        insights.append("Strong defensive involvement – high tackle activity.")
        if features["missed_tackles"] > 3:
            insights.append("⚠️ Needs work on tackle discipline (high misses).")
    elif label == "Playmaker":
        insights.append("High passing rate – likely key in distribution.")
    elif label == "Attacker":
        insights.append("High carry/run ratio – dangerous ball carrier.")
        if features["tackles"] > 5:
            insights.append("Also contributes well in defense.")

    return insights
