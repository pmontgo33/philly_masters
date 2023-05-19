from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import TeamForm
from .models import Golfer, Tournament


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
