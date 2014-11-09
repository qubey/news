from django.conf.urls import patterns, url
from trends import views

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),
  url(r'^search/(?P<query>[\w\s]+)$', views.search, name='search'),
  url(r'^stuff$', views.stuff, name='stuff'),
  url(r'^async/city/(?P<city>[\w\s,.]+)$', views.asyncCity, name='city'),
)
