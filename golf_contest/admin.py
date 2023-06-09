from django.contrib import admin

from .models import Golfer, Team, Tournament

admin.site.register(Tournament)
# admin.site.register(Golfer)
# admin.site.register(Team)


@admin.register(Golfer)
class GolferAdmin(admin.ModelAdmin):
    list_display = ["name", "tournament", "tournament_position", "score_to_par"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "tournament", "user"]
