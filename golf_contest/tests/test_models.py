import pytest

from golf_contest.models import Golfer


def test_golfer_create(db):
    new_golfer = Golfer.objects.create(name="Tiger Woods", tournament_position=2)
    assert Golfer.objects.count() == 1
    assert new_golfer.name == "Tiger Woods"
    assert new_golfer.tournament_position == 2


@pytest.fixture()
def golfer_1(db):
    return Golfer.objects.create(name="Jack Nicklaus", tournament_position=1)
