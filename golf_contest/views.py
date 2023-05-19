from django.shortcuts import render

from .forms import TeamForm
from .models import Tournament


def index(request):
    return render(request, "golf_contest/index.html", {})


def standings(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    teams = tournament.team_set.all()
    return render(request, "golf_contest/standings.html", {"tournament": tournament, "teams": teams})


def leaderboard(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    golfers = tournament.golfer_set.all()
    return render(request, "golf_contest/leaderboard.html", {"tournament": tournament, "golfers": golfers})


def team_new(request):
    form = TeamForm()
    return render(request, "golf_contest/team_new.html", {"form": form})
