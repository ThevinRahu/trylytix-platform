import os
import joblib
import pandas as pd

# --- Load all saved models and encoders ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

rf_model = joblib.load(os.path.join(BASE_DIR, '..', 'rugby_rf_model.pkl'))
gb_model = joblib.load(os.path.join(BASE_DIR, '..','rugby_gb_model.pkl'))
archetype_model = joblib.load(os.path.join(BASE_DIR, '..', 'rugby_archetype_rf_model.pkl'))
scaler = joblib.load(os.path.join(BASE_DIR, '..', 'rugby_scaler.pkl'))
label_encoder = joblib.load(os.path.join(BASE_DIR, '..', 'rugby_label_encoder.pkl'))
kmeans = joblib.load(os.path.join(BASE_DIR, '..', 'rugby_kmeans_archetypes.pkl'))

# --- Assume you have a function to get player features as a dict ---
def get_player_features(player_id):
    # Example stub, replace with real extraction
    # Should return a dict with all feature keys used during training
    return {
        # fill in all your feature columns here with values
        "weight": 102, "height": 188, "position": 4, "clean_breaks": 3, "conversion_goals": 0,
        "defenders_beaten": 4, "drop_goals_converted": 0, "kick_percent_success": 0, "kicks": 2,
        "kicks_from_hand": 1, "lineouts_won": 5, "lineout_won_steal": 1, "mauls_won": 3,
        "meters_run": 65, "missed_tackles": 1, "offload": 2, "passes": 13, "penalties_conceded": 1,
        "penalty_goals": 0, "points": 5, "red_cards": 0, "rucks_won": 7, "runs": 12, "tackles": 15,
        "total_free_kicks_conceded": 0, "total_lineouts": 6, "tries": 1, "try_assists": 1,
        "turnover_knock_on": 1, "turnovers_conceded": 2, "yellow_cards": 0,
        # Composite features (if used in training)
        "defensive_impact": 23, "attacking_threat": 12, "discipline": -1, "playmaking": 5
    }

def predict_player_all_models(player_id):
    features = get_player_features(player_id)
    X = pd.DataFrame([features])

    # Ensure column order matches what each model expects
    if hasattr(rf_model, "feature_names_in_"):
        X_rf = X.reindex(columns=rf_model.feature_names_in_, fill_value=0)
    else:
        X_rf = X

    if hasattr(gb_model, "feature_names_in_"):
        X_gb = X.reindex(columns=gb_model.feature_names_in_, fill_value=0)
    else:
        X_gb = X

    if hasattr(archetype_model, "feature_names_in_"):
        X_arch = X.reindex(columns=archetype_model.feature_names_in_, fill_value=0)
    else:
        X_arch = X

    # Scale
    X_rf_scaled = scaler.transform(X_rf)
    X_gb_scaled = scaler.transform(X_gb)
    X_arch_scaled = scaler.transform(X_arch)

    # Predict main label
    rf_pred = label_encoder.inverse_transform(rf_model.predict(X_rf_scaled))[0]
    gb_pred = label_encoder.inverse_transform(gb_model.predict(X_gb_scaled))[0]

    # Predict archetype (from model and from KMeans cluster)
    arch_pred = archetype_model.predict(X_arch_scaled)[0]
    kmeans_pred = kmeans.predict(X_arch[["defensive_impact", "attacking_threat", "discipline", "playmaking"]])[0]

    # Optionally, get prediction probabilities
    rf_probs = rf_model.predict_proba(X_rf_scaled)[0]
    gb_probs = gb_model.predict_proba(X_gb_scaled)[0]

    return {
        "rf_label": rf_pred,
        "gb_label": gb_pred,
        "rf_probabilities": dict(zip(label_encoder.classes_, rf_probs)),
        "gb_probabilities": dict(zip(label_encoder.classes_, gb_probs)),
        "archetype_model": arch_pred,
        "archetype_kmeans": int(kmeans_pred),
        "features_used": features
    }

# --- Example usage ---
def deep_rf_analysis(player_id):
    player_id = 123456  # Replace with actual player ID
    result = predict_player_all_models(player_id)
    return result