from django.urls import path
from .views import start_scrape

urlpatterns = [
    path("start-scrape/",start_scrape,name="scrape-codal"),
]
