from django.test import TestCase

from golf_contest.models import Golfer

# Create your tests here.


class GolferModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Golfer.objects.create(name="Tiger Woods", tournament_position=2)
        Golfer.objects.create(name="Jack Nicklaus", tournament_position=1)

    def test_golfer_name(self):
        self.assertEqual(Golfer.objects.get(id=1).name, "Tiger Woods")
        self.assertEqual(Golfer.objects.get(id=2).name, "Jack Nicklaus")

    def test_golfer_position(self):
        self.assertEqual(Golfer.objects.get(id=1).tournament_position, 2)
        self.assertEqual(Golfer.objects.get(id=2).tournament_position, 1)
