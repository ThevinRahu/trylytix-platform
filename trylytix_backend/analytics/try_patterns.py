import joblib
import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Model paths (adjust if necessary)
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'try_pattern_model.pkl')
LSTM_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'try_lstm_model.h5')

# Event type mapping (must match what you used for training)
EVENT_TYPE_LIST = [
    "try", "kick", "penalty", "kickoff", "pass", "carry", "run", "tackle", "missed_tackle", "ruck",
    "maul", "lineout", "lineout_win", "lineout_loss", "scrum", "scrum_win", "scrum_loss", "kick_return",
    "box_kick", "grubber_kick", "free_kick", "drop_goal", "conversion", "conversion_missed",
    "penalty_goal", "penalty_missed", "turnover", "knock_on", "forward_pass", "interception",
    "high_tackle", "offside", "not_releasing", "holding_on", "in_touch", "restart", "injury",
    "yellow_card", "red_card", "sin_bin", "substitution", "try_assist", "line_break",
    "defensive_line_break", "advantage", "offload", "foul_play", "referee_call", "timeout",
    "restart_22"
]
EVENT_TYPE2IDX = {e: i+1 for i, e in enumerate(EVENT_TYPE_LIST)}
maxlen = 10  # Must match what you used for training

def encode_event_seq(seq):
    """Encode event strings to integer list using EVENT_TYPE2IDX."""
    return [EVENT_TYPE2IDX.get(ev, 0) for ev in seq]

def predict_outcome(test_sequence):
    try:
        # Load models
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        if not os.path.exists(LSTM_MODEL_PATH):
            raise FileNotFoundError(f"LSTM model file not found at {LSTM_MODEL_PATH}")

        clf = joblib.load(MODEL_PATH)
        lstm_model = tf.keras.models.load_model(LSTM_MODEL_PATH)

        # Encode and pad sequence
        encoded = encode_event_seq(test_sequence)
        if len(encoded) < maxlen:
            padded = [0]*(maxlen - len(encoded)) + encoded
        else:
            padded = encoded[-maxlen:]
        padded_np = np.array(padded).reshape(1, -1)

        # Classic ML prediction
        rf_pred = clf.predict(padded_np)[0]
        rf_prob = clf.predict_proba(padded_np)[0][1]  # Probability for class 1 (try)

        # LSTM prediction
        lstm_padded = pad_sequences([encoded], maxlen=maxlen)
        lstm_probs = lstm_model.predict(lstm_padded)
        lstm_pred = int(np.argmax(lstm_probs, axis=1)[0])
        lstm_prob = float(lstm_probs[0][1])  # Probability for class 1 (try)

        return {
            "classic_ml": {
                "prediction": int(rf_pred),
                "probability": float(rf_prob)
            },
            "lstm": {
                "prediction": int(lstm_pred),
                "probability": float(lstm_prob)
            }
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Example input sequence (replace with your actual test data)
    test_sequence = ['kick', 'lineout', 'lineout_win', 'maul', 'offload']
    result = predict_outcome(test_sequence)
    print(result)