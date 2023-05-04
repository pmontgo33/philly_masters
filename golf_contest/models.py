import datetime

from django.conf import settings
from django.db import models

# Create your models here.


class Golfer(models.Model):
    name = models.CharField(max_length=30)
    tournament_position = models.PositiveSmallIntegerField(default=0)
    score_to_par = models.SmallIntegerField(default=0)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE)

    # Rounds
    rd_one_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_one_strokes = models.SmallIntegerField(default=0)
    rd_two_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_two_strokes = models.SmallIntegerField(default=0)
    rd_three_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_three_strokes = models.SmallIntegerField(default=0)
    rd_four_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_four_strokes = models.SmallIntegerField(default=0)

    # TODO Add @property for applicable world ranking

    def __str__(self):
        return self.name


class Tournament(models.Model):
    STATE_CHOICES = [
        ("NST", "Not Started"),
        ("RD1", "Round 1"),
        ("RD2", "Round 2"),
        ("RD3", "Round 3"),
        ("RD4", "Round 4"),
        ("FNL", "FINAL"),
    ]
    name = models.CharField(max_length=200)
    start_date = models.DateField(default=datetime.date.today)
    state = models.CharField(choices=STATE_CHOICES, max_length=3, default="NST")
    world_ranking_week = models.SmallIntegerField(default=0)

    @property
    def year(self):
        return self.start_date.year

    @property
    def champion(self):
        if self.state == "FNL":
            return self.golfer_set.get(tournament_position=1)
        else:
            return None

    def __str__(self):
        display_name = str(self.year) + " " + self.name
        return display_name


class Team(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey("Tournament", null=True, blank=True, on_delete=models.CASCADE)
    golfers = models.ManyToManyField("Golfer")

    def add_golfer(self, new_golfer):
        if self.golfers.count() < 5:
            if new_golfer.tournament == self.tournament:
                self.golfers.add(new_golfer)

    def __str__(self):
        return self.name
