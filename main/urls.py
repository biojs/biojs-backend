from django.conf.urls import url
from . import views

app_name = 'datatest'

urlpatterns = [
		url(r'^$', views.index, name="index"),
		url(r'^updatedata/$', views.update_data, name="update_data"),
]