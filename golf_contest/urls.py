from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tournament/<int:pk>/", views.standings, name="standings"),
    path("tournament/<int:pk>/leaderboard/", views.leaderboard, name="leaderboard"),
    path("tournament/<int:pk>/team/new/", views.NewTeamView.as_view(), name="team_new"),
    path("tournament/new/", views.NewTournamentView.as_view(), name="tournament_new"),
]
