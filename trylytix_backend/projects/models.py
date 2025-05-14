from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sport = models.CharField(max_length=50, default='rugby')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
