from django.urls import path
from locations import views

urlpatterns = [
    path("countries/", views.country_list),
    path("countries/<int:pk>/", views.country_detail),
]
