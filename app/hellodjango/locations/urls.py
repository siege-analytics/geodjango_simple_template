from django.urls import path
from rest_framework.routers import format_suffix_patterns
from locations import views

urlpatterns = [
    # GADM
    path("countries/", views.CountryList.as_view(), name="countries"),
    path("countries/<int:pk>/", views.CountryDetail.as_view(), name="country"),
    # Synthetics
    path("places/", views.PlaceList.as_view(), name="places"),
    path("places/<int:pk>/", views.PlaceDetail.as_view(), name="place"),
]

# this is licit
# new_urls = []
#
# urlpatterns.extend(new_urls)

urlpatterns = format_suffix_patterns(urlpatterns)
