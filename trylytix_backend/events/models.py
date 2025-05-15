from django.db import models
from matches.models import Match
from teams.models import Player, Team

class Event(models.Model):
    EVENT_TYPES = [
        ("pass", "Pass"),
        ("tackle", "Tackle"),
        ("try", "Try"),
        ("kick", "Kick"),
        ("penalty", "Penalty"),
        ("kickoff", "Kick-off"),
        ("pass", "Pass"),
        ("carry", "Carry"),
        ("run", "Run"),
        ("tackle", "Tackle"),
        ("missed_tackle", "Missed Tackle"),
        ("ruck", "Ruck"),
        ("maul", "Maul"),
        ("lineout", "Lineout"),
        ("lineout_win", "Lineout Win"),
        ("lineout_loss", "Lineout Loss"),
        ("scrum", "Scrum"),
        ("scrum_win", "Scrum Win"),
        ("scrum_loss", "Scrum Loss"),
        ("kick", "Kick"),
        ("kick_return", "Kick Return"),
        ("box_kick", "Box Kick"),
        ("grubber_kick", "Grubber Kick"),
        ("penalty", "Penalty"),
        ("free_kick", "Free Kick"),
        ("drop_goal", "Drop Goal"),
        ("try", "Try"),
        ("conversion", "Conversion"),
        ("conversion_missed", "Conversion Missed"),
        ("penalty_goal", "Penalty Goal"),
        ("penalty_missed", "Penalty Missed"),
        ("turnover", "Turnover"),
        ("knock_on", "Knock-on"),
        ("forward_pass", "Forward Pass"),
        ("interception", "Interception"),
        ("high_tackle", "High Tackle"),
        ("offside", "Offside"),
        ("not_releasing", "Not Releasing"),
        ("holding_on", "Holding On"),
        ("in_touch", "Ball in Touch"),
        ("restart", "Restart"),
        ("injury", "Injury"),
        ("yellow_card", "Yellow Card"),
        ("red_card", "Red Card"),
        ("sin_bin", "Sin Bin"),
        ("substitution", "Substitution"),
        ("try_assist", "Try Assist"),
        ("line_break", "Line Break"),
        ("defensive_line_break", "Defensive Line Break"),
        ("advantage", "Advantage"),
        ("offload", "Offload"),
        ("foul_play", "Foul Play"),
        ("referee_call", "Referee Call"),
        ("timeout", "Timeout"),
        ("restart_22", "22m Restart"),
    ]

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    opponent_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    timestamp = models.TimeField(null=True, blank=True)
    x_coord = models.FloatField(null=True, blank=True)
    y_coord = models.FloatField(null=True, blank=True)
    location_zone = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.event_type} by {self.player} at {self.timestamp}"
