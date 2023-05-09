import csv
import datetime

from django.conf import settings
from django.db import models
from django.db.models import Max, Sum

# Create your models here.


class Golfer(models.Model):
    name = models.CharField(max_length=40)
    tournament_position = models.CharField(null=True, blank=True, max_length=4)
    score_to_par = models.SmallIntegerField(null=True, blank=True, default=None)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE)

    # Rounds
    rd_one_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_one_strokes = models.SmallIntegerField(null=True, blank=True, default=None)
    rd_two_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_two_strokes = models.SmallIntegerField(null=True, blank=True, default=None)
    rd_three_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_three_strokes = models.SmallIntegerField(null=True, blank=True, default=None)
    rd_four_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_four_strokes = models.SmallIntegerField(null=True, blank=True, default=None)

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

    @staticmethod
    def get_tournament_from_csv():
        new_tournament = Tournament.objects.get(pk=2)
        new_tournament.save()
        with open("golf_contest/fixtures/2023_masters_leaderboard.csv") as f:
            for line in csv.DictReader(
                f, fieldnames=("position", "name", "score_to_par", "rd1", "rd2", "rd3", "rd4", "total_stokes")
            ):
                if line["score_to_par"] == "E":
                    line["score_to_par"] = 0
                elif line["score_to_par"] == "CUT" or line["score_to_par"] == "WD":
                    line["score_to_par"] = None

                if line["rd1"] == "":
                    line["rd1"] = None
                if line["rd2"] == "":
                    line["rd2"] = None
                if line["rd3"] == "":
                    line["rd3"] = None
                if line["rd4"] == "":
                    line["rd4"] = None
                new_golfer = Golfer.objects.create(
                    name=line["name"],
                    tournament_position=line["position"],
                    score_to_par=line["score_to_par"],
                    tournament=new_tournament,
                    rd_one_strokes=line["rd1"],
                    rd_two_strokes=line["rd2"],
                    rd_three_strokes=line["rd3"],
                    rd_four_strokes=line["rd4"],
                )
                new_golfer.save()

    def __str__(self):
        display_name = str(self.year) + " " + self.name
        return display_name


class Team(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey("Tournament", null=True, blank=True, on_delete=models.CASCADE)
    golfers = models.ManyToManyField("Golfer")

    @property
    def raw_score(self):
        if self.golfers.count() > 0:
            all_golfers_score = self.golfers.all().aggregate(Sum("score_to_par"))["score_to_par__sum"]
            worst_golfer_score = self.golfers.all().aggregate(Max("score_to_par"))["score_to_par__max"]
            return all_golfers_score - worst_golfer_score
        else:
            return 0

    @property
    def bonuses(self):
        return 0

    @property
    def score(self):
        return self.raw_score + self.bonuses

    @property
    def place(self):
        # Potential efficiency would be to only calculate this when the updated
        # Tournament leaderboard is pulled in, rather than at each request
        all_teams_in_tournament = self.tournament.team_set.all()
        all_teams_in_tournament = sorted(all_teams_in_tournament, key=lambda x: x.score)
        if sum(team.score == self.score for team in all_teams_in_tournament) > 1:
            for i, dic in enumerate(all_teams_in_tournament):
                if dic.score == self.score:
                    return "T" + str(i + 1)
        else:
            return all_teams_in_tournament.index(self) + 1

    def add_golfer(self, new_golfer):
        if self.golfers.count() < 5:
            if new_golfer.tournament == self.tournament:
                self.golfers.add(new_golfer)

    def __str__(self):
        return self.name
