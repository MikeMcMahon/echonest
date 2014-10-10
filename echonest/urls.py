from django.conf.urls import patterns, include, url
from django.contrib import admin
from echonest import views

urlpatterns = patterns('',
    url(r'^$', views.ingester)
)
