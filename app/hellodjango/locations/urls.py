from django.urls import path
from rest_framework.routers import format_suffix_patterns
from locations import views


urlpatterns = []

# There are a lot of URLs, so we're going to separate them into separate lists and then flatten into one..

gadm = [
    # GADM
    path(
        "admin_level_0s/", views.Admin_Level_0_List.as_view(), name="admin_level_0_list"
    ),
    path(
        "admin_level_0s/<int:pk>/",
        views.Admin_Level_0_Detail.as_view(),
        name="admin_level_0_detail",
    ),
    path(
        "admin_level_1s/", views.Admin_Level_1_List.as_view(), name="admin_level_1_list"
    ),
    path(
        "admin_level_1s/<int:pk>/",
        views.Admin_Level_1_Detail.as_view(),
        name="admin_level_1_detail",
    ),
    # Synthetics
    path("places/", views.PlaceList.as_view(), name="places_list"),
    path("places/<int:pk>/", views.PlaceDetail.as_view(), name="places_detail"),
    path("places/lookup/", views.Filtered_Place_List.as_view(), name="lookup"),
]


# this is licit
# new_urls = []
#
urlpatterns.extend(gadm)

urlpatterns = format_suffix_patterns(urlpatterns)
