import datetime

import pytest

from golf_contest.models import Golfer, Team, Tournament
from mysite.users.models import User

GOLFERS = [
    {
        "name": "Tiger Woods",
        "tournament_position": 1,
        "score_to_par": -18,
    },
    {
        "name": "Tom Kite",
        "tournament_position": 2,
        "score_to_par": -6,
    },
    {
        "name": "Tommy Tolles",
        "tournament_position": 3,
        "score_to_par": -5,
    },
    {
        "name": "Tom Watson",
        "tournament_position": 4,
        "score_to_par": -4,
    },
    {
        "name": "Costantino Rocca",
        "tournament_position": 5,
        "score_to_par": -3,
    },
    {
        "name": "Paul Stankowski",
        "tournament_position": 5,
        "score_to_par": -3,
    },
    {
        "name": "Fred Couples",
        "tournament_position": 7,
        "score_to_par": -2,
    },
    {
        "name": "Bernhard Langer",
        "tournament_position": 7,
        "score_to_par": -2,
    },
    {
        "name": "Justin Leonard",
        "tournament_position": 7,
        "score_to_par": -2,
    },
    {
        "name": "Davis Love III",
        "tournament_position": 7,
        "score_to_par": -2,
    },
    {
        "name": "Jeff Sluman",
        "tournament_position": 7,
        "score_to_par": -2,
    },
]


@pytest.fixture
def tournament_data(db):
    return Tournament.objects.create(
        name="Masters", start_date=datetime.date(year=2023, month=4, day=6), state="FNL", world_ranking_week=0, id=1
    )


@pytest.fixture
def golfer_data(db, tournament_data):
    data = []
    i = 1
    for golfer in GOLFERS:
        data.append(
            Golfer.objects.create(
                name=golfer["name"],
                tournament_position=golfer["tournament_position"],
                score_to_par=golfer["score_to_par"],
                tournament=tournament_data,
                id=i,
            )
        )
        i += 1
    return data


@pytest.fixture
def user_data(db):
    user1 = User.objects.create(email="user1@test.com")
    user1.set_password("password")
    user1.save()
    user2 = User.objects.create(email="user2@test.com")
    user2.set_password("password")
    user2.save()

    return [user1, user2]


@pytest.fixture
def team_data(user_data, tournament_data, golfer_data):
    team1 = Team.objects.create(name="Pimento Cheese", user=user_data[0], tournament=tournament_data, id=1)

    team1.add_golfer(golfer_data[1])
    team1.add_golfer(golfer_data[3])
    team1.add_golfer(golfer_data[5])
    team1.add_golfer(golfer_data[7])
    team1.add_golfer(golfer_data[9])
    team1.save()

    team2 = Team.objects.create(name="Maester Aemon Corner", user=user_data[1], tournament=tournament_data, id=2)

    team2.add_golfer(golfer_data[0])
    team2.add_golfer(golfer_data[2])
    team2.add_golfer(golfer_data[4])
    team2.add_golfer(golfer_data[6])
    team2.add_golfer(golfer_data[8])
    team2.save()

    return [team1, team2]


# @pytest.fixture(scope="session")
# def django_db_setup(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         call_command("loaddata", "golf_contest_data.json")
# call_command('loaddata', 'user_data.json')
