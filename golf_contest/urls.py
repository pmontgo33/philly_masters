from django.urls import path

from . import views

urlpatterns = [
    path("new_team/", views.new_team, name="new_team"),
]
