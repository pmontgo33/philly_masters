from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tournament/<int:pk>/", views.standings, name="standings"),
    path("leaderboard/<int:pk>/", views.leaderboard, name="leaderboard"),
    path("team/new", views.team_new, name="team_new"),
]
