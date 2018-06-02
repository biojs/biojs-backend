from django.conf.urls import url
from . import views

app_name = 'datatest'

urlpatterns = [
		url(r'^$', views.index, name="index"),
		url(r'^updatedata/$', views.update_data, name="update_data"),
		url(r'^all/$', views.all_components, name="all_components"),
        url(r'^top/$', views.top_components, name="top_components"),
        url(r'^details/(?P<url_name>\w+)/$', views.component_details, name="component_details"),
]