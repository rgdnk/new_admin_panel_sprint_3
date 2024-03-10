# Third Party
from django.urls import path

# First Party
from movies.api.v1 import views


urlpatterns = [
    path("movies/", views.MoviesListApi.as_view()),
    path("movies/<pk>/", views.MoviesDetailApi.as_view()),
]
