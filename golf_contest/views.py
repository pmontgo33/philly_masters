from django.shortcuts import render

from .models import Tournament


def index(request):
    return render(request, "golf_contest/index.html", {})


def standings(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    print(tournament)
    teams = tournament.team_set.all()
    print(teams)

    return render(request, "golf_contest/standings.html", {"tournament": tournament, "teams": teams})
