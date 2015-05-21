from django.conf.urls import patterns, include, url
from echonest import views

urlpatterns = patterns(
    '',
    url(r'^login/$', views.login),
    url(r'^$', views.ingester),
    url(r'^(unmatched|matched)/$', views.song_listing),
    url(r'^retry/(\d+)$', views.retry),
)
