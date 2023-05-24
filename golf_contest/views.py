import datetime

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import TeamForm, TournamentForm
from .models import Golfer, Tournament


def index(request):
    return render(request, "golf_contest/index.html", {})


def standings(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    teams = tournament.team_set.all()
    return render(request, "golf_contest/standings.html", {"tournament": tournament, "teams": teams, "pk": pk})


def leaderboard(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    golfers = tournament.golfer_set.all()
    return render(request, "golf_contest/leaderboard.html", {"tournament": tournament, "golfers": golfers, "pk": pk})


class NewTournamentView(FormView):
    template_name = "golf_contest/tournament_new.html"
    form_class = TournamentForm
    success_url = reverse_lazy("index")  # CREATE A TOURNAMENT VIEW PAGE THAT THIS REDIRECTS TO

    def form_valid(self, form):
        new_tournament = form.save(commit=False)

        # Pull Golfers from entry-list endpoint
        url = "https://golf-leaderboard-data.p.rapidapi.com/entry-list/" + str(new_tournament.tournament_id)
        headers = {
            "X-RapidAPI-Key": settings.GOLF_LEADERBOARD_API_KEY,
            "X-RapidAPI-Host": "golf-leaderboard-data.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers)

        tournament_data = response.json()["results"]["tournament"]
        # tournament_data = {
        #     "country": "Fort Worth, USA",
        #     "course": "Colonial Country Club",
        #     "end_date": "2023-05-28 00:00:00",
        #     "fund_currency": "USD",
        #     "id": 508,
        #     "name": "Charles Schwab Challenge",
        #     "prize_fund": "8700000",
        #     "start_date": "2023-05-25 00:00:00",
        #     "timezone": "America/Chicago",
        #     "tour_id": 2,
        #     "type": "Stroke Play",
        # }
        new_tournament.name = tournament_data["name"]
        new_tournament.start_date = datetime.datetime.strptime(tournament_data["start_date"], "%Y-%m-%d %H:%M:%S")

        if "live_details" in tournament_data.keys():
            new_tournament.status = tournament_data["live_details"]["status"]
            new_tournament.current_round = tournament_data["current_round"]
        else:
            new_tournament.status = "pre"
            new_tournament.current_round = 0

        new_tournament.save()
        return super().form_valid(form)


class NewTeamView(FormView):
    template_name = "golf_contest/team_new.html"
    form_class = TeamForm

    def get_initial(self):
        pk = self.kwargs["pk"]
        tournament = get_object_or_404(Tournament, pk=pk)
        self.success_url = reverse_lazy("standings", kwargs={"pk": pk})
        return {"tournament": tournament}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        pk = self.kwargs["pk"]
        kwargs["queryset"] = Golfer.objects.filter(tournament=Tournament.objects.get(pk=pk))
        return kwargs

    def form_valid(self, form):
        new_team = form.save()
        if form.is_valid():
            new_team.add_golfer(form.cleaned_data["golfer_1"])
            new_team.add_golfer(form.cleaned_data["golfer_2"])
            new_team.add_golfer(form.cleaned_data["golfer_3"])
            new_team.add_golfer(form.cleaned_data["golfer_4"])
            new_team.add_golfer(form.cleaned_data["golfer_5"])

        return super().form_valid(form)
