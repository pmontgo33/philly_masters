import requests
from celery import shared_task
from django.conf import settings

from golf_contest.models import Tournament


@shared_task
def update_create_leaderboard(tournament):
    url = "https://golf-leaderboard-data.p.rapidapi.com/entry-list/507"
    headers = {
        "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
        "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)

    print(response.json()["results"]["entry_list"])

    for golfer in response.json()["results"]["entry_list"]:
        player_id = golfer["player_id"]
        name = golfer["first_name"] + " " + golfer["last_name"]
        tournament.add_golfer(player_id=player_id, name=name)


@shared_task
def get_leaderboard():
    url = "https://golf-leaderboard-data.p.rapidapi.com/leaderboard/507"
    headers = {
        "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
        "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)

    print(response.json()["results"]["leaderboard"])


@shared_task
def count_tournaments():
    return Tournament.objects.count()
