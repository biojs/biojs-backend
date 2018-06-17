from django.shortcuts import render
from .serializers import *
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
import urllib, json
from django.core.management import call_command
from django.core.serializers.json import DjangoJSONEncoder

def index(request):
    top_downloaded_components = Component.objects.all().only('name', 'id', 'downloads', 'url_name').order_by('-downloads')[:3]
    top_starred_components = Component.objects.all().only('name', 'id', 'stars', 'url_name').order_by('-stars')[:3]
    recent_components = Component.objects.all().only('name', 'id', 'modified_time', 'url_name').order_by('-modified_time')[:3]
    downloaded = DownloadSerializer(top_downloaded_components, many=True)               # serialized data containing number of downloads
    starred = StarSerializer(top_starred_components, many=True)         # serialized data containing number of stars
    recent = RecentComponentSerializer(recent_components, many=True)
    return JsonResponse({
        'top_dl_components':downloaded.data,
        'top_starred_components':starred.data,
        'most_recent_components':recent.data,
        })

def all_components(request):    # requested on_load() for querying
    all_components = BaseComponentSerializer(Component.objects.all().only('name', 'id', 'url_name'), many=True)
    return JsonResponse({
        'all_components':all_components.data,
        })

def top_components(request):
    # Download data is from Github and hence stars are used
    top_components = TopComponentSerializer(Component.objects.all().order_by('-stars')[:10], many=True)
    return JsonResponse({
        'top_components':top_components.data,
        })

def component_details(request, url_name):
    component = Component.objects.get(url_name=url_name)
    details = DetailComponentSerializer(component, context={'request':request})
    contributions = ContributionSerializer(component.contributions, many=True)
    return JsonResponse({
        'details' : details.data,
        'contributors' : contributions.data,
    })

@staff_member_required
def update_data(request):
    call_command('updatecomponents')
    return HttpResponse("Database Successfully Updated.")