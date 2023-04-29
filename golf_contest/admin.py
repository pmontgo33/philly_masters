from django.contrib import admin

from .models import Golfer, Team, Tournament

admin.site.register(Tournament)
admin.site.register(Golfer)
admin.site.register(Team)
