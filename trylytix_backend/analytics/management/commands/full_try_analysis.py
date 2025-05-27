import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from django.core.management.base import BaseCommand
from events.models import Event

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import numpy as np

# For deep learning
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Masking
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import joblib

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
IDX2EVENT_TYPE = {v: k for k, v in EVENT_TYPE2IDX.items()}

def encode_event_seq(seq):
    return [EVENT_TYPE2IDX.get(ev, 0) for ev in seq]

class Command(BaseCommand):
    help = "Full rugby try analysis: descriptive, pattern mining, ML, deep learning"

    def add_arguments(self, parser):
        parser.add_argument('--team', type=str, default=None, help='Analyze tries scored by this team only')
        parser.add_argument('--opponent', type=str, default=None, help='Analyze tries scored against this team only')
        parser.add_argument('--n_events', type=int, default=5, help='Number of events before each try to analyze')
        parser.add_argument('--maxlen', type=int, default=10, help='Max sequence length for ML')

    def handle(self, *args, **options):
        team_name = options['team']
        opponent_name = options['opponent']
        n_events = options['n_events']
        maxlen = options['maxlen']
        print(f"Analyzing last {n_events} events before each try (max sequence length for ML: {maxlen})...")

        # 1. FETCH & PREP DATA
        qs = Event.objects.all().select_related("team", "player", "match")
        if team_name:
            qs = qs.filter(team__name=team_name)
        data = []
        for e in qs:
            data.append({
                'id': e.id,
                'match_id': e.match_id,
                'team_name': e.team.name if e.team else None,
                'player_id': e.player_id,
                'event_type': e.event_type,
                'timestamp': e.timestamp,
                'phase': e.phase,
                'x_coord': e.x_coord,
                'y_coord': e.y_coord,
                'location_zone': e.location_zone,
                'description': e.description,
            })
        df = pd.DataFrame(data)
        if df.empty:
            print("No events found for the given filter.")
            return

        # 2. DESCRIPTIVE ANALYTICS
        try_events = df[df['event_type'] == 'try']
        print(f"\nTotal tries: {len(try_events)}")
        print(f"Try breakdown by team:\n{try_events['team_name'].value_counts()}")
        print(f"Try breakdown by location_zone:\n{try_events['location_zone'].value_counts()}")

        # Try location heatmap
        try_locations = try_events[['x_coord','y_coord']].dropna()
        if not try_locations.empty:
            plt.figure(figsize=(8, 6))
            plt.hexbin(try_locations['x_coord'], try_locations['y_coord'], gridsize=20, cmap='Reds', bins='log')
            plt.xlabel('Field Length (x, 0=own try line, 100=opposition try line)')
            plt.ylabel('Field Width (y)')
            plt.title('Try Locations Heatmap')
            plt.colorbar(label='log(N tries)')
            plt.tight_layout()
            plt.savefig('try_locations_heatmap.png')
            print("Try location heatmap saved as try_locations_heatmap.png")

        # 3. PATTERN MINING
        patterns = []
        for idx, row in try_events.iterrows():
            match_id = row['match_id']
            team_name = row['team_name']
            ts = row['timestamp']
            prev_events = df[
                (df['match_id'] == match_id) &
                (df['team_name'] == team_name) &
                (df['timestamp'] < ts)
            ].sort_values('timestamp').tail(n_events)
            patterns.append(tuple(prev_events['event_type']))

        pattern_counts = Counter(patterns)
        print("\nMost common event patterns before a try:")
        for seq, count in pattern_counts.most_common(10):
            print(f"{seq}: {count} times")

        # 4. CLASSIC MACHINE LEARNING: Predict if sequence leads to try

        # (a) Build sequences (X) and targets (y)
        # For all sequences of maxlen events, label 1 if next event is try, else 0
        sequences = []
        labels = []
        for match_id in df['match_id'].unique():
            match_df = df[df['match_id'] == match_id].sort_values('timestamp')
            team_names = match_df['team_name'].unique()
            for team in team_names:
                team_df = match_df[match_df['team_name'] == team]
                evs = list(team_df['event_type'])
                for i in range(len(evs) - maxlen):
                    seq = evs[i:i+maxlen]
                    label = 1 if (i+maxlen < len(evs) and evs[i+maxlen] == 'try') else 0
                    sequences.append(seq)
                    labels.append(label)
        # Encode
        X = [encode_event_seq(seq) for seq in sequences]
        # Pad (shouldn't need, all maxlen)
        X = np.array(X)
        y = np.array(labels)

        if len(X) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            joblib.dump(clf, 'try_pattern_model.pkl')
            print("\nClassic ML (RandomForest):")
            print("Accuracy:", accuracy_score(y_test, y_pred))
            print(classification_report(y_test, y_pred))
        else:
            print("Not enough data for classic ML.")

        # 5. DEEP LEARNING: LSTM Sequence Model
        if len(X) > 0:
            vocab_size = len(EVENT_TYPE2IDX) + 2
            X_pad = pad_sequences(X, maxlen=maxlen)
            y_cat = to_categorical(y, 2)

            model = Sequential()
            model.add(Embedding(input_dim=vocab_size, output_dim=32, mask_zero=True, input_length=maxlen))
            model.add(LSTM(32, return_sequences=False))
            model.add(Dense(16, activation='relu'))
            model.add(Dense(2, activation='softmax'))
            model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            print("\nTraining LSTM deep learning model...")
            model.fit(X_pad, y_cat, batch_size=64, epochs=3, validation_split=0.2, verbose=2)
            scores = model.evaluate(X_pad, y_cat, verbose=0)
            print(f"LSTM model accuracy on all data: {scores[1]*100:.2f}%")
            model.save('try_lstm_model.h5')
            print("Saved LSTM deep learning model as try_lstm_model.h5")
        else:
            print("Not enough data for deep learning.")

        print("\nDone! You now have:")
        print("- Descriptive stats")
        print("- Pattern mining of events before tries")
        print("- Classic ML classifier for try-prediction")
        print("- LSTM deep learning model for sequence-based try prediction")
        print("- Try location heatmap PNG")
