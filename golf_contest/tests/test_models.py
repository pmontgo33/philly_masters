import datetime

import pytest

from golf_contest.models import Golfer, Tournament


@pytest.fixture
def new_golfer(db) -> Golfer:
    return Golfer.objects.create(name="Tiger Woods", tournament_position=2)


@pytest.fixture
def new_tournament(db) -> Tournament:
    return Tournament.objects.create(name="The Masters", start_date=datetime.date(year=2023, month=4, day=6))


def test_golfer_create(new_golfer):
    assert Golfer.objects.count() == 1
    assert new_golfer.name == "Tiger Woods"
    assert new_golfer.tournament_position == 2


def test_golfer_filter(new_golfer):
    assert Golfer.objects.filter(name="Tiger Woods").exists()


def test_golfer_update(new_golfer):
    new_golfer.name = "Jack Nicklaus"
    new_golfer.save()

    golfer_from_db = Golfer.objects.get(name="Jack Nicklaus")
    assert golfer_from_db.name == "Jack Nicklaus"


def test_tournament_create(new_tournament):
    assert Tournament.objects.count() == 1
    assert new_tournament.name == "The Masters"
    assert new_tournament.start_date == datetime.date(year=2023, month=4, day=6)


def test_tournament_filter(new_tournament):
    assert Tournament.objects.filter(name="The Masters").exists()


def test_tournament_update(new_tournament):
    new_tournament.name = "PGA Championship"
    new_tournament.save()

    tournament_from_db = Tournament.objects.get(name="PGA Championship")
    assert tournament_from_db.name == "PGA Championship"


def test_tournament_year_property(new_tournament):
    start_date_year = new_tournament.start_date.year
    assert new_tournament.year == start_date_year
