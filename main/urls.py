from django.conf.urls import url
from . import views

app_name = 'main'

urlpatterns = [
		url(r'^$', views.index, name="index"),
		url(r'^updatedata/$', views.update_data, name="update_data"),
		url(r'^all/$', views.all_components, name="all_components"),
        url(r'^top/$', views.top_components, name="top_components"),
        url(r'^details/(?P<url_name>[\w-]+)/$', views.component_details, name="component_details"),
		url(r'^visualization/(?P<url_name>[\w-]+)/(?P<visualization_name>[\w-]+)/$', views.render_visualization, name="render_visualization"),
		url(r'^random_snippets/$', views.generate_random_snippets, name='generate_random_snippets'),
]