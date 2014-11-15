from django.conf.urls import patterns, url
from trends import views

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),
  url(r'^search$', views.search, name='search'),
  url(r'^map$', views.stuff, name='stuff'),
  url(r'^async/city/(?P<city>[\w\s,.]+)$', views.asyncCity, name='city'),
)
