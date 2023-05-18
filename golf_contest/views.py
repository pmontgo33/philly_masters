from django.shortcuts import render

from .models import Tournament


def index(request):
    return render(request, "golf_contest/index.html", {})


def standings(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    teams = tournament.team_set.all()

    return render(request, "golf_contest/standings.html", {"tournament": tournament, "teams": teams})
