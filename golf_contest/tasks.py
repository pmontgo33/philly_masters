from datetime import datetime

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
        golfer.thru = golfer_data["holes_played"]

        round = next(r for r in golfer_data["rounds"] if r["round_number"] == 1)
        if round["tee_time_local"] is not None:
            golfer.rd_one_tee_time = datetime.strptime(round["tee_time_local"], "%H:%M")
        golfer.rd_one_strokes = round["strokes"]
        golfer.rd_one_score_to_par = round["total_to_par"]

        round = next(r for r in golfer_data["rounds"] if r["round_number"] == 2)
        if round["tee_time_local"] is not None:
            golfer.rd_two_tee_time = datetime.strptime(round["tee_time_local"], "%H:%M")
        golfer.rd_two_strokes = round["strokes"]
        golfer.rd_two_score_to_par = round["total_to_par"]

        round = next(r for r in golfer_data["rounds"] if r["round_number"] == 3)
        if round["tee_time_local"] is not None:
            golfer.rd_three_tee_time = datetime.strptime(round["tee_time_local"], "%H:%M")
        golfer.rd_three_strokes = round["strokes"]
        golfer.rd_three_score_to_par = round["total_to_par"]

        round = next(r for r in golfer_data["rounds"] if r["round_number"] == 4)
        if round["tee_time_local"] is not None:
            golfer.rd_four_tee_time = datetime.strptime(round["tee_time_local"], "%H:%M")
        golfer.rd_four_strokes = round["strokes"]
        golfer.rd_four_score_to_par = round["total_to_par"]

        golfer.save()

    for golfer in tournament.golfer_set.all():
        golfer.check_tied()
        golfer.save(update_fields=["tournament_position_tied"])

    for team in tournament.team_set.all():
        team.calculate_raw_score()
        team.save(update_fields=["raw_score"])

    for team in tournament.team_set.all():
        team.calculate_place()
        team.save(update_fields=["place", "place_tied"])
