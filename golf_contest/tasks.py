import requests
from celery import shared_task

from golf_contest.models import Tournament


@shared_task
def get_leaderboard():
    url = "https://golf-leaderboard-data.p.rapidapi.com/leaderboard/25"
    headers = {
        "X-RapidAPI-Key": "9cec043c71msh1498d7b1d12c51ap12687cjsnce1852b2a557",
        "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)

    print(response.json()["results"]["tournament"])


@shared_task
def count_tournaments():
    return Tournament.objects.count()
