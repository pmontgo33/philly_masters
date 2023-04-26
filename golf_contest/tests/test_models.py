import pytest

from golf_contest.models import Golfer


@pytest.mark.django_db
def test_golfer_create():
    Golfer.objects.create(name="Tiger Woods", tournament_position=2)
    assert Golfer.objects.count() == 1


@pytest.fixture()
def golfer_1(db):
    return Golfer.objects.create(name="Jack Nicklaus", tournament_position=1)
