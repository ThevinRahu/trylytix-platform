import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'outcome_model.pkl')

def predict_match_outcome(features: dict):
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)

        input_data = [[
            features['tackles'],
            features['missed_tackles'],
            features['passes'],
            features['tries'],
            features['penalties']
        ]]

        prediction = model.predict_proba(input_data)[0]
        label = model.predict(input_data)[0]

        label_map = {0: "loss", 1: "win", 2: "draw"}

        return {
            "prediction": label_map[label],
            "confidence": f"{max(prediction) * 100:.2f}%"
        }
    except Exception as e:
        return {"error": str(e)}
