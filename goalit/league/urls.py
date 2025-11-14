from django.urls import path
from . import views
from .views import MatchListView

app_name = "league"

urlpatterns = [
    path("", views.MatchListView.as_view(), name="match_list"),
    path("<int:pk>/", views.match_detail, name="match_detail"),
    path("<int:pk>/join/", views.join_match, name="join_match"),
    path("<int:pk>/leave/", views.leave_match, name="leave_match"),
    path("<int:pk>/set-status/", views.set_status, name="set_status"),  # Going/Maybe/Not
    path("<int:pk>/set-team/", views.set_team, name="set_team"),        # manual team assign (organizer)
    path("<int:pk>/finalize/", views.finalize_match, name="finalize_match"),  # set final score + attendance
]
