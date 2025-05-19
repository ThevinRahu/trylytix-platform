from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from events.models import Event
from teams.models import Player, Team
from matches.models import Match
from analytics.ml_model_prediction import predict_match_outcome
from analytics.player_analysis import deep_rf_analysis

@api_view(['GET'])
def player_stats(request, player_id):
    stats = (
        Event.objects.filter(player_id=player_id)
        .values('event_type')
        .annotate(count=Count('id'))
    )
    return Response({
        "player_id": player_id,
        "event_counts": stats
    })

@api_view(['GET'])
def team_stats(request, team_id):
    stats = (
        Event.objects.filter(team_id=team_id)
        .values('event_type')
        .annotate(count=Count('id'))
    )
    return Response({
        "team_id": team_id,
        "event_counts": stats
    })

@api_view(['GET'])
def match_summary(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        return Response({'error': 'Match not found'}, status=404)

    events = Event.objects.filter(match=match)

    # Per team breakdown
    team_stats = (
        events.values('team__name', 'event_type')
        .annotate(count=Count('id'))
    )

    # Top players by involvement
    top_players = (
        events.values('player__full_name')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    return Response({
        'match_id': match_id,
        'home_team': match.home_team.name,
        'away_team': match.away_team.name,
        'team_stats': team_stats,
        'top_players': top_players
    })

@api_view(['GET'])
def match_heatmap(request, match_id):
    team_id = request.query_params.get('team')
    player_id = request.query_params.get('player')

    filters = {'match_id': match_id}
    if team_id:
        filters['team_id'] = team_id
    if player_id:
        filters['player_id'] = player_id

    coords = Event.objects.filter(**filters).values(
        'x_coord',
        'y_coord',
        'event_type',
        'timestamp',
        'location_zone',
        'description',
        'player_id'
    )

    return Response({
        'match_id': match_id,
        'points': list(coords)
    })

@api_view(['GET'])
def player_advanced_stats(request, player_id):
    events = Event.objects.filter(player_id=player_id)

    total = events.count()
    stats = events.values('event_type').annotate(count=Count('id'))

    tackles = events.filter(event_type='tackle').count()
    missed = events.filter(event_type='missed_tackle').count()
    try_assists = events.filter(event_type='try_assist').count()
    carries = events.filter(event_type='carry').count()
    passes = events.filter(event_type='pass').count()

    return Response({
        "player_id": player_id,
        "total_events": total,
        "tackles": tackles,
        "missed_tackles": missed,
        "tackle_success_rate": f"{round((tackles / (tackles + missed) * 100), 1) if (tackles + missed) > 0 else 'N/A'}%",
        "passes": passes,
        "carries": carries,
        "try_assists": try_assists,
        "event_breakdown": list(stats),
    })

from matches.models import Match

@api_view(['GET'])
def team_trend_stats(request, team_id):
    matches = Match.objects.filter(
        home_team_id=team_id
    ) | Match.objects.filter(
        away_team_id=team_id
    )

    trend = []

    for match in matches:
        events = Event.objects.filter(match=match, team_id=team_id)
        tackles = events.filter(event_type='tackle').count()
        missed = events.filter(event_type='missed_tackle').count()
        tries = events.filter(event_type='try').count()
        passes = events.filter(event_type='pass').count()
        penalties = events.filter(event_type='penalty').count()

        opponent = match.away_team if match.home_team_id == team_id else match.home_team

        trend.append({
            "match_id": match.id,
            "date": match.date,
            "opponent": opponent.name,
            "tackles": tackles,
            "missed_tackles": missed,
            "success_rate": f"{round((tackles / (tackles + missed) * 100), 1) if (tackles + missed) > 0 else 'N/A'}%",
            "tries": tries,
            "passes": passes,
            "penalties": penalties
        })

    return Response({
        "team_id": team_id,
        "trend": trend
    })

@api_view(['GET'])
def team_tactical_suggestions(request, team_id):
    suggestions = []

    matches = Match.objects.filter(
        home_team_id=team_id
    ) | Match.objects.filter(
        away_team_id=team_id
    )

    for match in matches:
        events = Event.objects.filter(match=match, team_id=team_id)
        tackles = events.filter(event_type='tackle').count()
        missed = events.filter(event_type='missed_tackle').count()
        passes = events.filter(event_type='pass').count()
        carries = events.filter(event_type='carry').count()
        penalties = events.filter(event_type='penalty').count()

        match_suggestions = []

        # Rule 1
        if missed > 5:
            match_suggestions.append("Too many missed tackles — improve defensive positioning.")

        # Rule 2
        if tackles + missed > 0:
            success_rate = tackles / (tackles + missed)
            if success_rate < 0.6:
                match_suggestions.append("Tackle success rate below 60% — focus on contact drills.")

        # Rule 3
        if penalties > 3:
            match_suggestions.append("High number of penalties — work on discipline in breakdown.")

        # Rule 4
        if carries > 0 and passes / carries < 0.8:
            match_suggestions.append("Low pass-to-carry ratio — consider better ball movement.")

        if match_suggestions:
            suggestions.append({
                "match_id": match.id,
                "opponent": match.away_team.name if match.home_team_id == team_id else match.home_team.name,
                "date": match.date,
                "recommendations": match_suggestions
            })

    return Response({
        "team_id": team_id,
        "tactical_suggestions": suggestions
    })

@api_view(['GET'])
def export_match_events(request, match_id):
    from events.models import Event
    from matches.models import Match

    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        return Response({"error": "Match not found"}, status=404)

    events = Event.objects.filter(match=match).values(
        'event_type',
        'timestamp',
        'x_coord',
        'y_coord',
        'location_zone',
        'description',
        'player__id',
        'player__full_name',
        'team__id',
        'team__name',
    )

    return Response({
        "match_id": match.id,
        "home_team": match.home_team.name,
        "away_team": match.away_team.name,
        "date": match.date,
        "events": list(events)
    })

@api_view(['POST'])
def predict_outcome(request):
    required = ['tackles', 'missed_tackles', 'passes', 'tries', 'penalties']
    for r in required:
        if r not in request.data:
            return Response({"error": f"{r} is required"}, status=400)

    prediction = predict_match_outcome(request.data)
    return Response(prediction)

@api_view(['GET'])
def player_ml_profile(request, player_id):
    data = deep_rf_analysis(player_id)
    return Response(data)


