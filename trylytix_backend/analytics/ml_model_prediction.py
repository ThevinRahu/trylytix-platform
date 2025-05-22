import joblib
import os
import pandas as pd
import numpy as np

# Model paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'outcome_model.pkl')
HOME_SCORE_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'home_score_model.pkl')
AWAY_SCORE_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'away_score_model.pkl')
FEATURES_PATH = os.path.join(os.path.dirname(__file__), '..', 'feature_columns.pkl')

def predict_match_outcome(features: dict, home_team: str, away_team: str):
    try:
        # Load models and features
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        if not os.path.exists(HOME_SCORE_MODEL_PATH):
            raise FileNotFoundError(f"Home score model file not found at {HOME_SCORE_MODEL_PATH}")
        if not os.path.exists(AWAY_SCORE_MODEL_PATH):
            raise FileNotFoundError(f"Away score model file not found at {AWAY_SCORE_MODEL_PATH}")
        if not os.path.exists(FEATURES_PATH):
            raise FileNotFoundError(f"Feature columns file not found at {FEATURES_PATH}")

        clf = joblib.load(MODEL_PATH)
        home_score_model = joblib.load(HOME_SCORE_MODEL_PATH)
        away_score_model = joblib.load(AWAY_SCORE_MODEL_PATH)
        feature_columns = joblib.load(FEATURES_PATH)

        # Prepare input row with all features set to 0
        input_dict = {col: 0 for col in feature_columns}
        for key, value in features.items():
            if key in input_dict:
                input_dict[key] = value

        # Set one-hot team columns if present
        home_col = f'home_team_{home_team}'
        away_col = f'away_team_{away_team}'
        if home_col in input_dict:
            input_dict[home_col] = 1
        if away_col in input_dict:
            input_dict[away_col] = 1

        input_df = pd.DataFrame([input_dict], columns=feature_columns)

        # Predict win/loss
        prediction = clf.predict(input_df)[0]
        proba = clf.predict_proba(input_df)[0]
        label_map = {0: "Away Win", 1: "Home Win"}

        # Predict scores
        home_score = home_score_model.predict(input_df)[0]
        away_score = away_score_model.predict(input_df)[0]

        return {
            "prediction": label_map[prediction],
            "confidence": f"{max(proba) * 100:.2f}%",
            "predicted_scores": {
                "home_team": home_team,
                "home_score": round(home_score),
                "away_team": away_team,
                "away_score": round(away_score)
            }
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Example: Blues vs NSW Waratahs match data
    features = {
    'home_clean_breaks': 9,
    'away_clean_breaks': 3,
    'home_conversion_goals': 1,
    'away_conversion_goals': 1,
    'home_defenders_beaten': 26,
    'away_defenders_beaten': 9,
    'home_kick_percent_success': 40.0,
    'away_kick_percent_success': 80.0,
    'home_kicks': 22,
    'away_kicks': 32,
    'home_kicks_from_hand': 635,
    'away_kicks_from_hand': 986,
    'home_lineouts_won': 13,
    'away_lineouts_won': 7,
    'home_lineout_won_steal': 3,
    'away_lineout_won_steal': 2,
    'home_mauls_total': 1,
    'away_mauls_total': 3,
    'home_mauls_won': 1,
    'away_mauls_won': 3,
    'home_meters_run': 499,
    'away_meters_run': 403,
    'home_missed_tackles': 9,
    'away_missed_tackles': 26,
    'home_offload': 10,
    'away_offload': 1,
    'home_passes': 144,
    'away_passes': 172,
    'home_pc_possession_first': 56,
    'home_pc_possession_second': 35,
    'away_pc_possession_first': 44,
    'away_pc_possession_second': 65,
    'home_pc_territory_first': np.nan,  # Data not available
    'home_pc_territory_second': np.nan,  # Data not available
    'away_pc_territory_first': np.nan,  # Data not available
    'away_pc_territory_second': np.nan,  # Data not available
    'home_penalties_conceded': 9,
    'away_penalties_conceded': 7,
    'home_penalty_goals': 1,
    'away_penalty_goals': 3,
    'home_possession': 45,
    'away_possession': 55,
    'home_red_cards': 0,
    'away_red_cards': 0,
    'home_rucks_total': 99,
    'away_rucks_total': 140,
    'home_rucks_won': 91,
    'away_rucks_won': 138,
    'home_runs': 126,
    'away_runs': 150,
    'home_scrums_total': 4,
    'away_scrums_total': 9,
    'home_scrums_won': 3,
    'away_scrums_won': 8,
    'home_tackles': 217,
    'away_tackles': 168,
    'home_territory': np.nan,  # Data not available
    'away_territory': np.nan,  # Data not available
    'home_total_free_kicks_conceded': np.nan,  # Data not available
    'away_total_free_kicks_conceded': np.nan,  # Data not available
    'home_total_lineouts': 16,
    'away_total_lineouts': 9,
    'home_tries': 3,
    'away_tries': 2,
    'home_turnover_knock_on': np.nan,  # Data not available
    'away_turnover_knock_on': np.nan,  # Data not available
    'home_turnovers_conceded': 22,
    'away_turnovers_conceded': 12,
    'home_yellow_card': 0,
    'away_yellow_card': 0,
    }

    home_team = "Blues"
    away_team = "Brumbies"
    result = predict_match_outcome(features, home_team, away_team)
    print(result)