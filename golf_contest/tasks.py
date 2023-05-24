import requests
from celery import shared_task
from django.conf import settings

from golf_contest.models import Golfer, Tournament


@shared_task
def update_leaderboard_golfers(tournament_pk):
    # Before tee times are set, entry list has the best list of golfers in the tournament.
    # After tee times are set, leaderboard may have golfers that entry list does not, so this
    # pulls golfers from both.

    tournament = Tournament.objects.get(pk=tournament_pk)

    # Pull Golfers from entry-list endpoint
    url = "https://golf-leaderboard-data.p.rapidapi.com/entry-list/" + str(tournament.tournament_id)
    headers = {
        "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
        "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)

    for golfer in response.json()["results"]["entry_list"]:
        player_id = golfer["player_id"]
        name = golfer["first_name"] + " " + golfer["last_name"]
        tournament.add_golfer(player_id=player_id, name=name)

    # Pull Golfers from leaderboard endpoint
    url = "https://golf-leaderboard-data.p.rapidapi.com/leaderboard/" + str(tournament.tournament_id)
    headers = {
        "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
        "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)

    for golfer in response.json()["results"]["leaderboard"]:
        player_id = golfer["player_id"]
        name = golfer["first_name"] + " " + golfer["last_name"]
        tournament.add_golfer(player_id=player_id, name=name)

    for golfer in tournament.golfer_set.all():
        # check if the golfer is in the
        if (
            next(
                (item for item in response.json()["results"]["leaderboard"] if item["player_id"] == golfer.player_id),
                None,
            )
            is None
        ):
            print(golfer.name)
            golfer.delete()


@shared_task
def update_leaderboard_scores(tournament_pk):
    tournament = Tournament.objects.get(pk=tournament_pk)

    url = "https://golf-leaderboard-data.p.rapidapi.com/leaderboard/" + str(tournament.tournament_id)
    headers = {
        "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
        "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)

    tournament.status = response.json()["results"]["tournament"]["live_details"]["status"]
    tournament.current_round = response.json()["results"]["tournament"]["live_details"]["current_round"]
    tournament.save(update_fields=["status", "current_round"])

    for golfer_data in response.json()["results"]["leaderboard"]:
        golfer = Golfer.objects.get(tournament=tournament, player_id=golfer_data["player_id"])
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

    tournament.update_leaderboard()


def test(tournament_pk):
    tournament = Tournament.objects.get(pk=tournament_pk)
    low_scores = {}
    rounds_complete = 0
    if tournament.status == "completed":
        rounds_complete = 4
    elif tournament.status == "endofday":
        rounds_complete = tournament.current_round
    else:
        rounds_complete = tournament.current_round - 1

    thru_exclude = ["CUT", "WD"]
    for i in range(rounds_complete):
        round_key = "r" + str(i + 1)
        golfers = tournament.golfer_set.exclude(thru__in=thru_exclude)
        low_golfer = min(golfers, key=lambda x: x.rounds[round_key]["strokes"])
        low_scores.update({round_key: low_golfer.rounds[round_key]["strokes"]})
    print(low_scores)
