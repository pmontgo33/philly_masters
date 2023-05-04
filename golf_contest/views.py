from django.shortcuts import render


def new_team(request):
    return render(request, "golf_contest/new_team.html", {})
