from django.db import models

# Create your models here.


class Golfer(models.Model):
    name = models.CharField(max_length=200)
    tournament_position = models.PositiveSmallIntegerField(default=0)
    score_to_par = models.SmallIntegerField(default=0)

    # TODO Add field tournament = models.ForeignKey('Tournament') after Tournament is created

    # Rounds
    rd_one_tee_time = models.TimeField(default="8:00")
    rd_one_strokes = models.SmallIntegerField(default=0)
    rd_two_tee_time = models.TimeField(default="8:00")
    rd_two_strokes = models.SmallIntegerField(default=0)
    rd_three_tee_time = models.TimeField(default="8:00")
    rd_three_strokes = models.SmallIntegerField(default=0)
    rd_four_tee_time = models.TimeField(default="8:00")
    rd_four_strokes = models.SmallIntegerField(default=0)

    # TODO Add @property for applicable world ranking


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
    start_date = models.DateField()
    state = models.CharField(choices=STATE_CHOICES, max_length=3)
    world_ranking_week = models.SmallIntegerField(default=1)

    @property
    def year(self):
        return self.start_date.year()
