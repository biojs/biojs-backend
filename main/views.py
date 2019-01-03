from django.shortcuts import render
from .serializers import *
from rest_framework.renderers import JSONRenderer
from management.commands.updatecomponents import send_GET_request
from django.http import JsonResponse, HttpResponseServerError
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
import urllib, json
from django.core.management import call_command
from django.core.serializers import serialize
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.paginator import Paginator
import numpy as np
import logging

logger = logging.getLogger()

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

def components(request):
    size = request.GET.get('size', 20)
    page = request.GET.get('page', 1)
    components_list = Component.objects.all().order_by('-modified_time')
    paginator = Paginator(components_list, size)
    serialised = TopComponentSerializer(paginator.page(page), many=True)
    return JsonResponse({
        'components': serialised.data
        })

def component_details(request, url_name):
    component = Component.objects.get(url_name=url_name)
    details = DetailComponentSerializer(component, context={'request':request})
    contributions = ContributionSerializer(component.contributions, many=True)
    js_dependencies = JSDependencySerializer(component.jsdependency_set.all(), many=True)
    css_dependencies = CSSDependencySerializer(component.cssdependency_set.all(), many=True)
    try:
        sniper_data = component.sniperdata
        sniper = SniperDataSerializer(sniper_data)
        snippets = SnippetSerializer(sniper_data.snippet_set.all(), many=True)
        return JsonResponse({
            'details' : details.data,
            'contributors' : contributions.data,
            'js_dependencies' : js_dependencies.data,
            'css_dependencies' : css_dependencies.data,
            'sniper_data' : sniper.data,
            'snippets' : snippets.data,
        })
    except:
        return JsonResponse({
            'details' : details.data,
            'contributors' : contributions.data,
            'js_dependencies' : js_dependencies.data,
            'css_dependencies' : css_dependencies.data,
        })

@xframe_options_exempt
def render_visualization(request, url_name, visualization_name):
    try:
        component = Component.objects.get(url_name=url_name)
        js_dependencies = component.jsdependency_set.all()
        css_dependencies = component.cssdependency_set.all()
        sniper_data = component.sniperdata
        snippet = Snippet.objects.get(sniperData=sniper_data, name=visualization_name)
        response = send_GET_request(snippet.url)
        script = response.read()
        serializer = DetailComponentSerializer(component).data
        component_data = JSONRenderer().render(serializer)
        js_deps_json = serialize('json', js_dependencies)
        css_deps_json = serialize('json', css_dependencies)
        context = {
            'component' : component_data,
            'js_dependencies' : js_deps_json,
            'css_dependencies' : css_deps_json,
            'snippet' : snippet,
            'snippet_script' : script,
            'sniper_data' : sniper_data,
            'no_browserify': sniper_data.no_browserify
        }
        # return HttpResponse()
        return render(request, 'main/visualizations.html', context)
    except Exception as e:
        print('Error in visualisation!', e)
        return HttpResponseServerError(e)

@staff_member_required
def update_data(request):
    call_command('updatecomponents')
    return HttpResponse("Database Successfully Updated.")

def generate_random_snippets(request):
    try:
        count = request.GET.get('q')
        if int(count) > Component.objects.filter(sniperdata__isnull=False).count():
            return JsonResponse({'error':'Input number q must not exceed %s.'%str(Component.objects.filter(sniperdata__isnull=False).count())})
        components = Component.objects.filter(sniperdata__isnull=False)
        required_components = np.random.choice(components, int(count), replace=False)
        return JsonResponse({'components':BaseComponentSerializer(required_components, many=True).data})
    except:
        return JsonResponse({'error':'Input number as query q in the URL.'})