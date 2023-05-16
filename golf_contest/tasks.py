import requests
from celery import shared_task
from django.conf import settings

from golf_contest.models import Tournament


@shared_task
def get_leaderboard():
    url = "https://golf-leaderboard-data.p.rapidapi.com/leaderboard/25"
    headers = {
        "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
        "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)

    print(response.json()["results"]["tournament"])


@shared_task
def count_tournaments():
    return Tournament.objects.count()
