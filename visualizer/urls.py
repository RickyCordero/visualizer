from django.urls import path

from visualizer.views import (
    APILinkStreamView,
    IndexView,
)

urlpatterns = [
    # relative to the tweetstream app
    path('',                             IndexView.as_view(),                         name="index-view"),
    path('link/',                        APILinkStreamView.as_view(),                 name="api-link-view"),
]