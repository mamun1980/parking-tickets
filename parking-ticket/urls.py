from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'tgis.views.home', name='home'),        
    url(r'^test/$', 'tgis.views.test', name='test'),
    url(r'^getlaw/$', 'tgis.views.getLaw', name='getLaw'),
)