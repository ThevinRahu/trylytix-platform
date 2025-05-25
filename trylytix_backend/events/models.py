from django.db import models
from matches.models import Match
from teams.models import Player, Team

class Event(models.Model):
    EVENT_TYPES = [
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
        ("kick_return", "Kick Return"),
        ("box_kick", "Box Kick"),
        ("grubber_kick", "Grubber Kick"),
        ("free_kick", "Free Kick"),
        ("drop_goal", "Drop Goal"),
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
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    is_opponent_event = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True, blank=True)
    x_coord = models.FloatField(null=True, blank=True, help_text="X coordinate, e.g., 0-100 along field length")
    y_coord = models.FloatField(null=True, blank=True, help_text="Y coordinate, e.g., 0-100 along field width")
    location_zone = models.CharField(max_length=50, blank=True, help_text="Named zone, e.g., '22', 'left wing', etc.")
    phase = models.PositiveIntegerField(null=True, blank=True, help_text="Phase of play leading up to event")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.event_type} by {self.player} at {self.timestamp}"

    class Meta:
        ordering = ['timestamp']