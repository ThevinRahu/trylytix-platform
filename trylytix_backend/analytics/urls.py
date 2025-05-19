from django.urls import path
from .views import export_match_events, match_heatmap, player_advanced_stats, player_stats, predict_outcome, team_stats, team_tactical_suggestions, team_trend_stats, player_ml_profile
from .views import match_summary

urlpatterns = [
    path('players/<int:player_id>/stats/', player_stats),
    path('teams/<int:team_id>/stats/', team_stats),
    path('matches/<int:match_id>/summary/', match_summary),
    path('matches/<int:match_id>/heatmap/', match_heatmap),
    path('players/<int:player_id>/advanced-stats/', player_advanced_stats),
    path('teams/<int:team_id>/trend/', team_trend_stats),
    path('teams/<int:team_id>/tactical-suggestions/', team_tactical_suggestions),
    path('matches/<int:match_id>/events-export/', export_match_events),
    path('predict-outcome/', predict_outcome),
    path('players/<int:player_id>/deep-analysis/', player_ml_profile),
]
