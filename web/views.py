from _datetime import datetime as dt

from django.http import HttpResponse
from django.shortcuts import render


def main_view(request):
    year = dt.now().year
    return render(request, "web/main.html", {
        "year": year
    })
