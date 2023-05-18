import csv
import datetime

from django.conf import settings
from django.db import models
from django.db.models import Max, Sum

from mysite.users.models import User

# Create your models here.


class Golfer(models.Model):
    player_id = models.IntegerField()
    name = models.CharField(max_length=40)
    tournament_position = models.CharField(null=True, blank=True, max_length=4)
    tournament_position_tied = models.BooleanField(default=False)
    score_to_par = models.SmallIntegerField(null=True, blank=True, default=None)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE)

    # Rounds
    rd_one_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_one_strokes = models.SmallIntegerField(null=True, blank=True, default=0)
    rd_two_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_two_strokes = models.SmallIntegerField(null=True, blank=True, default=0)
    rd_three_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_three_strokes = models.SmallIntegerField(null=True, blank=True, default=0)
    rd_four_tee_time = models.TimeField(null=True, blank=True, default=None)
    rd_four_strokes = models.SmallIntegerField(null=True, blank=True, default=0)

    # TODO Add @property for applicable world ranking

    class Meta:
        unique_together = ("player_id", "tournament")

    @property
    def total_strokes(self):
        return self.rd_one_strokes + self.rd_two_strokes + self.rd_three_strokes + self.rd_four_strokes

    @property
    def position_with_ties(self):
        if self.tournament_position_tied:
            return "T" + str(self.tournament_position)
        else:
            return str(self.tournament_position)

    def check_tied(self):
        all_golfers_in_tournament = self.tournament.golfer_set.all()
        all_golfers_in_tournament = sorted(all_golfers_in_tournament, key=lambda x: x.score_to_par)
        if sum(golfer.score_to_par == self.score_to_par for golfer in all_golfers_in_tournament) > 1:
            for i, dic in enumerate(all_golfers_in_tournament):
                if dic.score_to_par == self.score_to_par:
                    self.tournament_position_tied = True
                    break
        else:
            self.tournament_position_tied = False

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
    tournament_id = models.IntegerField()
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

    def add_golfer(self, player_id, name):
        Golfer.objects.update_or_create(player_id=player_id, tournament=self, defaults={"name": name})

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
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tournament = models.ForeignKey("Tournament", null=True, blank=True, on_delete=models.CASCADE)
    golfers = models.ManyToManyField("Golfer")

    raw_score = models.SmallIntegerField(default=0)
    bonuses = models.SmallIntegerField(default=0)
    place = models.PositiveSmallIntegerField(null=True, blank=True, default=None)
    place_tied = models.BooleanField(default=False)

    @property
    def score(self):
        return self.raw_score + self.bonuses

    @property
    def place_with_ties(self):
        if self.place_tied:
            return "T" + str(self.place)
        else:
            return str(self.place)

    def calculate_place(self):
        all_teams_in_tournament = self.tournament.team_set.all()
        all_teams_in_tournament = sorted(all_teams_in_tournament, key=lambda x: x.score)
        if sum(team.score == self.score for team in all_teams_in_tournament) > 1:
            for i, dic in enumerate(all_teams_in_tournament):
                if dic.score == self.score:
                    self.place = i + 1
                    self.place_tied = True
                    break
        else:
            self.place = all_teams_in_tournament.index(self) + 1
            self.place_tied = False

    def calculate_raw_score(self):
        if self.golfers.count() > 0:
            all_golfers_score = self.golfers.all().aggregate(Sum("score_to_par"))["score_to_par__sum"]
            worst_golfer_score = self.golfers.all().aggregate(Max("score_to_par"))["score_to_par__max"]
            self.raw_score = all_golfers_score - worst_golfer_score
        else:
            self.raw_score = 0

    def add_golfer(self, new_golfer):
        if self.golfers.count() < 5:
            if new_golfer.tournament == self.tournament:
                self.golfers.add(new_golfer)

    @staticmethod
    def get_teams_from_csv():
        new_tournament = Tournament.objects.get(pk=2)
        new_tournament.save()
        with open("golf_contest/fixtures/team_data.csv") as f:
            i = 1
            for line in csv.DictReader(
                f,
                fieldnames=(
                    "name",
                    "participant_name",
                    "golfer_1",
                    "golfer_2",
                    "golfer_3",
                    "golfer_4",
                    "golfer_5",
                    "third_tie_breaker",
                ),
            ):
                new_team = Team.objects.create(
                    name=line["name"],
                    user=User.objects.get(pk=i),
                    tournament=new_tournament,
                )
                new_team.save()

                print(line["golfer_1"])
                new_golfer = Golfer.objects.get(name=line["golfer_1"], tournament=new_tournament)
                new_team.add_golfer(new_golfer)
                new_golfer = Golfer.objects.get(name=line["golfer_2"], tournament=new_tournament)
                new_team.add_golfer(new_golfer)
                new_golfer = Golfer.objects.get(name=line["golfer_3"], tournament=new_tournament)
                new_team.add_golfer(new_golfer)
                new_golfer = Golfer.objects.get(name=line["golfer_4"], tournament=new_tournament)
                new_team.add_golfer(new_golfer)
                new_golfer = Golfer.objects.get(name=line["golfer_5"], tournament=new_tournament)
                new_team.add_golfer(new_golfer)

                if i == 1:
                    i = 2
                elif i == 2:
                    i = 3
                else:
                    i = 1

    def __str__(self):
        return self.name
