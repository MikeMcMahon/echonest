from django.conf.urls import patterns, include, url
from echonest import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ingester),
    url(r'^(unmatched|matched)/$', views.song_listing)
)
