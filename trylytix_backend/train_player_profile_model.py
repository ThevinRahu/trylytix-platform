import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
from rugbypy.player import fetch_player_stats


def aggregate_player_stats(stats_df):
    numeric_cols = [
        "rucks_won", "runs", "tackles", "total_free_kicks_conceded", "total_lineouts",
        "tries", "try_assists", "turnover_knock_on", "turnovers_conceded", "yellow_cards"
    ]
    agg = stats_df[numeric_cols].fillna(0).astype(float).sum()
    return {col: int(agg[col]) for col in numeric_cols}

def extract_features(player_stats):
    return {
        "rucks_won": int(player_stats.get("rucks_won", 0)),
        "runs": int(player_stats.get("runs", 0)),
        "tackles": int(player_stats.get("tackles", 0)),
        "total_free_kicks_conceded": int(player_stats.get("total_free_kicks_conceded", 0)),
        "total_lineouts": int(player_stats.get("total_lineouts", 0)),
        "tries": int(player_stats.get("tries", 0)),
        "try_assists": int(player_stats.get("try_assists", 0)),
        "turnover_knock_on": int(player_stats.get("turnover_knock_on", 0)),
        "turnovers_conceded": int(player_stats.get("turnovers_conceded", 0)),
        "yellow_cards": int(player_stats.get("yellow_cards", 0)),
    }

def generate_label(features):
    def to_scalar(x):
        # Handles Series, numpy values, etc.
        if isinstance(x, (pd.Series, np.ndarray)):
            return x.item() if x.size == 1 else x[0]  # or raise an error
        return x

    tackles = to_scalar(features["tackles"])
    rucks_won = to_scalar(features["rucks_won"])
    tries = to_scalar(features["tries"])
    try_assists = to_scalar(features["try_assists"])
    yellow_cards = to_scalar(features["yellow_cards"])
    turnover_knock_on = to_scalar(features["turnover_knock_on"])
    turnovers_conceded = to_scalar(features["turnovers_conceded"])

    insights = []
    if tackles > 10:
        insights.append("Very strong defender.")
    if rucks_won > 5:
        insights.append("Excellent at contesting rucks.")
    if tries > 1:
        insights.append("Dangerous try-scorer.")
    if try_assists > 1:
        insights.append("Playmaking skills evident.")
    if yellow_cards > 0:
        insights.append("Disciplinary issues (yellow cards).")
    if turnover_knock_on > 2:
        insights.append("Needs to reduce handling errors (knock-ons).")
    if turnovers_conceded > 2:
        insights.append("High turnover rate.")
    if not insights:
        insights.append("Well-rounded with no standout strengths or weaknesses.")
    return " ".join(insights)

# 1. Sample dataset — You can build this from actual DB later
player_ids = ['238367', '302117', '301864', '300726', '300670', '300616',
       '298707', '298543', '297076', '296207', '295126', '294359',
       '293879', '292160', '292154', '291379', '288451', '285669',
       '245267', '243185', '237657', '177474', '176339', '304191',
       '303220', '302949', '300419', '299032', '296940', '294081',
       '292751', '290928', '290892', '290887', '286559', '255075',
       '212319', '206907', '176284', '174185', '172276', '172266',
       '165154', '147695', '136556', '125388', '158721', '301191',
       '299481', '299280', '299169', '298786', '294809', '292682',
       '291347', '285607', '278697', '265603', '255949', '239597',
       '228559', '228531', '228205', '227763', '215295', '184451',
       '158712', '134164', '125385', '158708', '302184', '301497',
       '301383', '301050', '300916', '300681', '299022', '298999',
       '298514', '297155', '297154', '296096', '295850', '295323',
       '295064', '290933', '283653', '239153', '212729', '212725',
       '176654', '165096', '298855', '301913', '298527', '296080',
       '295194', '292699', '292592', '292591', '285691', '285683',
       '258957', '212583', '194469', '172719', '169067', '165575',
       '158701', '158698', '145340', '134573', '134572', '96413', '15972',
       '290946', '301432', '300475', '299147', '299031', '298470',
       '296843', '296841', '295853', '294374', '294037', '292217',
       '291648', '290914', '290913', '290431', '289392', '288779',
       '285791', '255181', '176112', '159211', '154534', '296957',
       '302842', '301480', '298777', '104729', '292227', '126149',
       '105490', '292164', '255963', '296848', '246117', '291693',
       '107693']  # Add as needed
data = []

for pid in player_ids:
    stats = fetch_player_stats(player_id=pid)
    print(f"DEBUG: stats for player {pid}: type={type(stats)}\n{stats}\n")
    if isinstance(stats, pd.DataFrame):
        features = aggregate_player_stats(stats)
    elif isinstance(stats, pd.Series):
        features = extract_features(stats.to_dict())
    elif isinstance(stats, dict):
        features = extract_features(stats)
    else:
        raise ValueError(f"Unknown stats type for player {pid}: {type(stats)}")
    label = generate_label(features)
    row = [
        features["rucks_won"],
        features["runs"],
        features["tackles"],
        features["total_free_kicks_conceded"],
        features["total_lineouts"],
        features["tries"],
        features["try_assists"],
        features["turnover_knock_on"],
        features["turnovers_conceded"],
        features["yellow_cards"],
        label
    ]
    data.append(row)

df = pd.DataFrame(data, columns=[
    'rucks_won', 'runs', 'tackles', 'total_free_kicks_conceded',
    'total_lineouts', 'tries', 'try_assists', 'turnover_knock_on',
    'turnovers_conceded', 'yellow_cards', 'label'
])

X = df.drop('label', axis=1)
y = df['label']

# Encode textual labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Normalize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y_encoded)

# Save model, scaler, and label encoder
joblib.dump(model, 'player_profile_rf_model.pkl')
joblib.dump(scaler, 'player_profile_scaler.pkl')
joblib.dump(le, 'player_profile_label_encoder.pkl')

print("✅ Model, scaler, and label encoder saved.")