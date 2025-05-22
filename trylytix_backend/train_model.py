import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score, classification_report
import joblib

# 1. Load data
df = pd.read_csv("match_data.csv")

# 2. Feature engineering
df['home_win'] = (df['winner'] == df['home_team']).astype(int)
df['home_score'] = ((df['home_conversion_goals'] * 2) + (df['home_tries'] * 5) + (df['home_penalty_goals'] * 3)).astype(int)
df['away_score'] = ((df['away_conversion_goals'] * 2) + (df['away_tries'] * 5) + (df['away_penalty_goals'] * 3)).astype(int)
df = pd.get_dummies(df, columns=['home_team', 'away_team'])

# 3. Select features (exclude scores and winner/home_win for regression/classification)
features = [col for col in df.columns if col not in ['winner', 'home_win', 'date', 'round', 'home_score', 'away_score']]
X = df[features]
y_win = df['home_win']
y_home = df['home_score']
y_away = df['away_score']

# 4. Split data (same split for all targets)
X_train, X_test, y_win_train, y_win_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
    X, y_win, y_home, y_away, test_size=0.2, random_state=42
)

# 5. Train models
home_win_clf = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
home_score_reg = xgb.XGBRegressor()
away_score_reg = xgb.XGBRegressor()

home_win_clf.fit(X_train, y_win_train)
home_score_reg.fit(X_train, y_home_train)
away_score_reg.fit(X_train, y_away_train)

# 6. Predict and evaluate
y_win_pred = home_win_clf.predict(X_test)
y_home_pred = home_score_reg.predict(X_test)
y_away_pred = away_score_reg.predict(X_test)

print("Home Win Accuracy:", accuracy_score(y_win_test, y_win_pred))
print(classification_report(y_win_test, y_win_pred))
print("Home Score MAE:", mean_absolute_error(y_home_test, y_home_pred))
print("Away Score MAE:", mean_absolute_error(y_away_test, y_away_pred))

# 7. Save models
joblib.dump(home_win_clf, 'outcome_model.pkl')
joblib.dump(home_score_reg, 'home_score_model.pkl')
joblib.dump(away_score_reg, 'away_score_model.pkl')
joblib.dump(list(X.columns), 'feature_columns.pkl')