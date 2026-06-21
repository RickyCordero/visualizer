from django.urls import path

from visualizer.views import (
    api_link_stream_view,
    IndexView,
)

urlpatterns = [
    # relative to the tweetstream app
    path('',                             IndexView.as_view(),                         name="index-view"),
    path('link/',                        api_link_stream_view,                        name="api-link-view"),
]