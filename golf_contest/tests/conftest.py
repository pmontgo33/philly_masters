import json
from datetime import datetime

import pytest

from golf_contest.models import Golfer, Team, Tournament
from mysite.users.models import User


@pytest.fixture
def load_fixture_files():
    f = open("golf_contest/fixtures/golf_data.json", "rb")
    data = json.load(f)
    f.close()
    return data


@pytest.fixture
def tournament_data(db, load_fixture_files):
    fixture_tournaments = [x for x in load_fixture_files if x["model"] == "golf_contest.tournament"]
    all_tournaments = []
    for tournament in fixture_tournaments:
        all_tournaments.append(
            Tournament.objects.create(
                name=tournament["fields"]["name"],
                tournament_id=tournament["fields"]["tournament_id"],
                start_date=datetime.strptime(tournament["fields"]["start_date"], "%Y-%m-%d"),
                status=tournament["fields"]["status"],
                world_ranking_week=tournament["fields"]["world_ranking_week"],
                current_round=tournament["fields"]["current_round"],
                id=tournament["pk"],
            )
        )
    return all_tournaments


@pytest.fixture
def golfer_data(db, load_fixture_files, tournament_data):
    fixture_golfers = [x for x in load_fixture_files if x["model"] == "golf_contest.golfer"]
    all_golfers = []

    for golfer in fixture_golfers:
        all_golfers.append(
            Golfer.objects.create(
                name=golfer["fields"]["name"],
                player_id=golfer["fields"]["player_id"],
                tournament_position=golfer["fields"]["tournament_position"],
                score_to_par=golfer["fields"]["score_to_par"],
                tournament=Tournament.objects.get(id=golfer["fields"]["tournament"]),
                id=golfer["pk"],
            )
        )
    return all_golfers


@pytest.fixture
def user_data(db, load_fixture_files):
    fixture_users = [x for x in load_fixture_files if x["model"] == "users.user"]
    all_users = []

    for user in fixture_users:
        all_users.append(
            User.objects.create(
                email=user["fields"]["email"],
                password=user["fields"]["password"],
                id=user["pk"],
            )
        )
    return all_users


@pytest.fixture
def team_data(user_data, tournament_data, golfer_data):
    team1 = Team.objects.create(name="Pimento Cheese", user=user_data[0], tournament=tournament_data[0], id=1)

    team1.add_golfer(golfer_data[1])
    team1.add_golfer(golfer_data[3])
    team1.add_golfer(golfer_data[5])
    team1.add_golfer(golfer_data[7])
    team1.add_golfer(golfer_data[9])
    team1.save()

    team2 = Team.objects.create(name="Maester Aemon Corner", user=user_data[1], tournament=tournament_data[0], id=2)

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
