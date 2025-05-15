from django.db import models
from projects.models import Project
from teams.models import Team

class Match(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    date = models.DateField()
    venue = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.date}"
