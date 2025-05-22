import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
import joblib
from rugbypy.player import fetch_player_stats

# --- CONFIGURATION ---

PLAYER_IDS = ['238367', '302117', '301864', '300726', '300670', '300616',
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
       '107693'] 

ALL_FIELDS = [
    'weight', 'height', 'position', 'clean_breaks', 'conversion_goals',
    'defenders_beaten', 'drop_goals_converted', 'kick_percent_success', 'kicks',
    'kicks_from_hand', 'lineouts_won', 'lineout_won_steal', 'mauls_won',
    'meters_run', 'missed_tackles', 'offload', 'passes', 'penalties_conceded',
    'penalty_goals', 'points', 'red_cards', 'rucks_won', 'runs', 'tackles',
    'total_free_kicks_conceded', 'total_lineouts', 'tries', 'try_assists',
    'turnover_knock_on', 'turnovers_conceded', 'yellow_cards'
]
COMPOSITE_FEATURES = [
    'defensive_impact', 'attacking_threat', 'discipline', 'playmaking'
]

# --- FEATURE EXTRACTION ---

def extract_all_features(player_stats):
    if isinstance(player_stats, pd.Series):
        player_stats = player_stats.to_dict()
    return {field: player_stats.get(field, 0) for field in ALL_FIELDS}

# --- ADVANCED LABELING LOGIC ---

def get_label_columns(features):
    """Return a dictionary of rugby insight labels based on stat patterns."""
    # Defensive Impact: tackles, rucks won, turnovers
    defensive = int(features.get('tackles', 0)) + int(features.get('rucks_won', 0)) + int(features.get('lineout_won_steal', 0))
    # Attacking Threat: tries, meters run, clean breaks, defenders beaten
    attacking = int(features.get('tries', 0)) + int(features.get('meters_run', 0)) // 10 + int(features.get('clean_breaks', 0)) + int(features.get('defenders_beaten', 0))
    # Discipline: negative impact of cards and penalties
    discipline = -(int(features.get('yellow_cards', 0)) * 2 + int(features.get('red_cards', 0)) * 5 + int(features.get('penalties_conceded', 0)))
    # Playmaking: try assists, offloads, passes
    playmaking = int(features.get('try_assists', 0)) * 2 + int(features.get('offload', 0)) + int(features.get('passes', 0)) // 10

    return {
        'defensive_impact': defensive,
        'attacking_threat': attacking,
        'discipline': discipline,
        'playmaking': playmaking
    }

def make_human_readable_labels(row):
    """Create a readable label string from composite features."""
    insights = []
    if row['defensive_impact'] > 20:
        insights.append("Elite Defender")
    elif row['defensive_impact'] > 10:
        insights.append("Strong Defender")
    if row['attacking_threat'] > 15:
        insights.append("Dangerous Attacker")
    elif row['attacking_threat'] > 7:
        insights.append("Solid Attacker")
    if row['playmaking'] > 10:
        insights.append("Creative Playmaker")
    if row['discipline'] < -5:
        insights.append("Disciplinary Issues")
    elif row['discipline'] > -2:
        insights.append("Disciplined Player")
    if not insights:
        insights.append("Well-rounded")
    return ", ".join(insights)

data = []
for pid in PLAYER_IDS:
    stats = fetch_player_stats(player_id=pid)
    if isinstance(stats, pd.DataFrame):
        agg = {}
        for field in ALL_FIELDS:
            if field in stats:
                try:
                    agg[field] = stats[field].fillna(0).astype(float).sum()
                except Exception:
                    agg[field] = stats[field].fillna("").astype(str).iloc[0]
            else:
                agg[field] = 0
        features = extract_all_features(agg)
    elif isinstance(stats, (pd.Series, dict)):
        features = extract_all_features(stats)
    else:
        raise ValueError(f"Unknown stats type for player {pid}: {type(stats)}")
    label_cols = get_label_columns(features)
    row = [features[field] for field in ALL_FIELDS] + [label_cols[k] for k in COMPOSITE_FEATURES]
    data.append(row)

df = pd.DataFrame(data, columns=ALL_FIELDS + COMPOSITE_FEATURES)

# --- CATEGORICAL ENCODING ---

if 'position' in df:
    df['position'] = LabelEncoder().fit_transform(df['position'].astype(str))

# --- HUMAN READABLE LABELS ---

df['label'] = df.apply(make_human_readable_labels, axis=1)

# --- ML DATA PREP ---

X = df[ALL_FIELDS + COMPOSITE_FEATURES]
y = df['label']

# --- SCALE NUMERIC FEATURES ---

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- CLUSTERING FOR ARCHETYPES ---

n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
df['archetype'] = kmeans.fit_predict(df[COMPOSITE_FEATURES])

# --- ENCODE LABELS ---

le_label = LabelEncoder()
y_encoded = le_label.fit_transform(y)

# --- MODELS ---

# 1. Random Forest for label prediction (multi-class)
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_scaled, y_encoded)

# 2. Gradient Boosting as alternative
gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
gb_model.fit(X_scaled, y_encoded)

# 3. Archetype classifier (predict cluster/archetype)
archetype_model = RandomForestClassifier(n_estimators=100, random_state=42)
archetype_model.fit(X_scaled, df['archetype'])

# --- EVALUATE (OPTIONAL) ---

print("RF Accuracy (cross-val):", cross_val_score(rf_model, X_scaled, y_encoded, cv=5).mean())
print("GB Accuracy (cross-val):", cross_val_score(gb_model, X_scaled, y_encoded, cv=5).mean())
print("Archetype Clusters:", df['archetype'].value_counts())

# --- SAVE ARTIFACTS ---

joblib.dump(rf_model, 'rugby_rf_model.pkl')
joblib.dump(gb_model, 'rugby_gb_model.pkl')
joblib.dump(archetype_model, 'rugby_archetype_rf_model.pkl')
joblib.dump(scaler, 'rugby_scaler.pkl')
joblib.dump(le_label, 'rugby_label_encoder.pkl')
joblib.dump(kmeans, 'rugby_kmeans_archetypes.pkl')
df.to_csv('rugby_players_full_dataset.csv', index=False)

print("✅ All models, encoders, and dataset saved.")

# --- SAMPLE USAGE ---

# To predict labels/archetypes:
# features = ...  # new player stats dict
# x = pd.DataFrame([extract_all_features(features)])[ALL_FIELDS + COMPOSITE_FEATURES]
# x['position'] = LabelEncoder().fit_transform(x['position'].astype(str))
# x_scaled = scaler.transform(x)
# label_pred = le_label.inverse_transform(rf_model.predict(x_scaled))
# archetype_pred = kmeans.predict(x[COMPOSITE_FEATURES])
# 1. Team predictions - get average of all events of both teams and use model to predict
# 2. Player stats
# 3. Attacking patterns strenghts/weaknesses
# 4. Defensive patterns strengths/weaknesses
