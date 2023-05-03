import datetime

from golf_contest.models import Golfer, Team, Tournament

# @pytest.fixture
# def new_tournament(db) -> Tournament:
#     return Tournament.objects.create(name="Philly", start_date=datetime.date(year=2023, month=4, day=6))


# @pytest.fixture
# def new_golfer(db, new_tournament) -> Golfer:
#     return Golfer.objects.create(name="Tiger Woods", tournament=new_tournament)


# @pytest.fixture
# def new_team(db) -> Team:
#     # TODO Need to create test users somehow.
#     user1 = User.objects.get(pk=1)
#     team = Team.objects.create(name="Pimento Cheese", user=user1)
#     team.tournament = Tournament.objects.get(pk=1)

#     for i in range(5):
#         team.add_golfer(Golfer.objects.get(pk=1))
#     team.save()


def test_golfer_create(golfer_data):
    assert Golfer.objects.count() > 0


def test_golfer_filter(golfer_data):
    assert Golfer.objects.filter(name="Tiger Woods").exists()


def test_golfer_update(golfer_data):
    my_golfer = Golfer.objects.get(name="Fred Couples")
    my_golfer.name = "Smiley Kaufman"
    my_golfer.save()

    golfer_from_db = Golfer.objects.get(name="Smiley Kaufman")
    assert golfer_from_db.name == "Smiley Kaufman"


def test_golfer_tee_time_blank(golfer_data):
    my_golfer = Golfer.objects.get(name="Fred Couples")
    assert my_golfer.rd_one_tee_time is None


def test_tournament_contains_golfer(golfer_data, tournament_data):
    my_golfer = Golfer.objects.get(name="Fred Couples")
    assert tournament_data.golfer_set.filter(name=my_golfer.name).exists()


def test_golfer_references_tournament(golfer_data, tournament_data):
    my_golfer = Golfer.objects.get(name="Fred Couples")
    assert my_golfer.tournament == tournament_data


def test_tournament_create(tournament_data):
    assert Tournament.objects.count() > 0
    assert tournament_data.name == "Masters"
    assert tournament_data.start_date == datetime.date(year=2023, month=4, day=6)


def test_tournament_filter(tournament_data):
    assert Tournament.objects.filter(name="Masters").exists()


def test_tournament_update(tournament_data):
    tournament_data.name = "PGA Championship"
    tournament_data.save()

    tournament_from_db = Tournament.objects.get(name="PGA Championship")
    assert tournament_from_db.name == "PGA Championship"


def test_tournament_year_property(tournament_data):
    start_date_year = tournament_data.start_date.year
    assert tournament_data.year == start_date_year


def test_team_create(team_data):
    assert Team.objects.count() > 0


def test_team_update(team_data):
    team_data[0].name = "Top Golf"
    team_data[0].save()

    team_from_db = Team.objects.get(name="Top Golf")
    assert team_from_db.name == "Top Golf"
