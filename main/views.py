from django.shortcuts import render
from .serializers import *
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

def index(request):
    top_dl_components = Component.objects.all().order_by('-downloads')[:3]
    top_starred_components = Component.objects.all().order_by('-stars')[:3]
    recent_components = Component.objects.all().order_by('-modified_time')[:3]
    dl = DownloadSerializer(top_dl_components, many=True)               # serialized data containing number of downloads
    starred = StarSerializer(top_starred_components, many=True)         # serialized data containing number of stars
    recent = RecentComponentSerializer(recent_components, many=True)    # serialized data according to upload time
    return JsonResponse({
        'top_dl_components':dl.data,
        'top_starred_components':starred.data,
        'most_recent_components':recent.data,
        })

@staff_member_required
def update_data(request):
    for component in Component.objects.all(): ### More to come here
            print component.name
    return HttpResponse("Database Successfully Updated.")