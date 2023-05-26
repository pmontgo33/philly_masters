import csv
import datetime

import requests
from django.conf import settings
from django.db import models
from django.db.models import Max, Sum

from mysite.users.models import User


class Golfer(models.Model):
    player_id = models.IntegerField()
    name = models.CharField(max_length=40)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE)
    tournament_position = models.CharField(null=True, blank=True, max_length=4)
    tournament_position_tied = models.BooleanField(default=False)
    score_to_par = models.SmallIntegerField(null=True, blank=True, default=None)
    thru = models.CharField(max_length=20, default="")
    score_today = models.SmallIntegerField(null=True, blank=True, default=None)

    # Rounds
    rounds = models.JSONField(
        default={
            "r1": {"tee_time": "", "strokes": "", "score_to_par": None},
            "r2": {"tee_time": "", "strokes": "", "score_to_par": None},
            "r3": {"tee_time": "", "strokes": "", "score_to_par": None},
            "r4": {"tee_time": "", "strokes": "", "score_to_par": None},
        }
    )

    # TODO Add @property for applicable world ranking

    class Meta:
        unique_together = ("player_id", "tournament")
        ordering = ["name"]

    @property
    def total_strokes(self):
        strokes = 0
        for key, value in self.rounds.items():
            strokes += value["strokes"]
        return strokes

    @property
    def position_with_ties(self):
        if self.tournament_position_tied:
            return "T" + str(self.tournament_position)
        else:
            return str(self.tournament_position)

    @property
    def score_to_par_formatted(self):
        if self.score_to_par == 0:
            return "E"
        elif self.score_to_par > 0:
            return "+" + str(self.score_to_par)
        else:
            return self.score_to_par

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

    def save(self, *args, **kwargs):
        if self.tournament.current_round > 0:
            current_round = "r" + str(self.tournament.current_round)
            self.score_today = self.rounds[current_round]["score_to_par"]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    tournament_id = models.IntegerField()
    start_date = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=15, default="pre")
    current_round = models.PositiveSmallIntegerField(default=0)
    world_ranking_week = models.SmallIntegerField(default=0)

    @property
    def year(self):
        return self.start_date.year

    @property
    def champion(self):
        if self.status == "completed":
            return self.golfer_set.get(tournament_position=1)
        else:
            return None

    def add_golfer(self, player_id, name):
        Golfer.objects.update_or_create(player_id=player_id, tournament=self, defaults={"name": name})

    def low_scores_completed_rounds(self):
        low_scores = {}
        rounds_complete = 0
        if self.status == "completed":
            rounds_complete = 4
        elif self.status == "endofday":
            rounds_complete = self.current_round
        else:
            rounds_complete = self.current_round - 1

        thru_exclude = ["CUT", "WD"]
        for i in range(rounds_complete):
            round_key = "r" + str(i + 1)
            golfers = self.golfer_set.exclude(thru__in=thru_exclude)
            low_golfer = min(golfers, key=lambda x: x.rounds[round_key]["strokes"])
            low_scores.update({round_key: low_golfer.rounds[round_key]["strokes"]})

        return low_scores

    def new_update_golfers(self):
        # Before tee times are set, entry list has the best list of golfers in the tournament.
        # After tee times are set, leaderboard may have golfers that entry list does not, so this
        # pulls golfers from both.

        # Pull Golfers from entry-list endpoint
        url = "https://golf-leaderboard-data.p.rapidapi.com/entry-list/" + str(self.tournament_id)
        headers = {
            "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
            "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers)

        for golfer in response.json()["results"]["entry_list"]:
            player_id = golfer["player_id"]
            name = golfer["first_name"] + " " + golfer["last_name"]
            self.add_golfer(player_id=player_id, name=name)

        # Pull Golfers from leaderboard endpoint
        url = "https://golf-leaderboard-data.p.rapidapi.com/leaderboard/" + str(self.tournament_id)
        headers = {
            "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
            "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers)

        for golfer in response.json()["results"]["leaderboard"]:
            player_id = golfer["player_id"]
            name = golfer["first_name"] + " " + golfer["last_name"]
            self.add_golfer(player_id=player_id, name=name)

        for golfer in self.golfer_set.all():
            # check if the golfer is in the
            if (
                next(
                    (
                        item
                        for item in response.json()["results"]["leaderboard"]
                        if item["player_id"] == golfer.player_id
                    ),
                    None,
                )
                is None
            ):
                golfer.delete()

    def new_update_scores(self):
        url = "https://golf-leaderboard-data.p.rapidapi.com/leaderboard/" + str(self.tournament_id)
        headers = {
            "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
            "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers)

        self.status = response.json()["results"]["tournament"]["live_details"]["status"]
        self.current_round = response.json()["results"]["tournament"]["live_details"]["current_round"]
        self.save(update_fields=["status", "current_round"])

        for golfer_data in response.json()["results"]["leaderboard"]:
            golfer = Golfer.objects.get(tournament=self, player_id=golfer_data["player_id"])
            golfer.tournament_position = golfer_data["position"]
            golfer.score_to_par = golfer_data["total_to_par"]

            if golfer_data["status"] == "active":
                golfer.thru = golfer_data["holes_played"]
            elif golfer_data["status"] == "between rounds":
                golfer.thru = ""  # MAKE THIS TEE TIME
            elif golfer_data["status"] == "complete":
                golfer.thru = "F"
            elif golfer_data["status"] == "endofday":
                golfer.thru = "F"
            else:
                golfer.thru = golfer_data["status"].upper()

            for round in golfer_data["rounds"]:
                round_number = "r" + str(round["round_number"])
                golfer.rounds[round_number]["strokes"] = round["strokes"]
                golfer.rounds[round_number]["tee_time"] = round["tee_time_local"]
                golfer.rounds[round_number]["score_to_par"] = round["total_to_par"]

            golfer.save()

        self.leaderboard_calculations()

    def leaderboard_calculations(self):
        # Check if golfers are tied
        for golfer in self.golfer_set.all():
            golfer.check_tied()
            golfer.save(update_fields=["tournament_position_tied"])

        # Calculate raw scores and bonuses for each team in the tournament
        low_scores = self.low_scores_completed_rounds()
        for team in self.team_set.all():
            team.calculate_raw_score()
            team.calculate_bonuses(low_scores)
            team.save(update_fields=["raw_score", "bonuses"])

        # Calculate the place for each team in the tournament
        for team in self.team_set.all():
            team.calculate_place()
            team.save(update_fields=["place", "place_tied"])

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

    def calculate_bonuses(self, low_scores):
        bonuses = 0
        for golfer in self.golfers.all():
            for key, value in low_scores.items():
                if golfer.rounds[key]["strokes"] == value:
                    bonuses -= 2
            if golfer == self.tournament.champion:
                bonuses -= 2

        self.bonuses = bonuses

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
