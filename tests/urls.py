from django.urls import include, path

urlpatterns = [
    path("tamara/", include("tamara.urls")),
]
