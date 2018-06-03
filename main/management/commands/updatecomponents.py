from django.core.management import BaseCommand
import urllib2, json, urllib
from main.models import *
from biojs.config import *
from datetime import datetime
import pytz

def get_github_data(github_url):
    response = urllib.urlopen(github_url)
    data = json.load(response)
    return data

def get_npm_data():
    # response = urllib2.urlopen()
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    req = urllib2.Request("http://registry.npmjs.com/-/v1/search?text=keywords:biojs,bionode&size=500", headers=hdr)
    response = urllib2.urlopen(req)
    data = json.load(response)
    return data

def get_contributors_data(contributors_url):
    response = urllib.urlopen(contributors_url)
    data = json.load(response)
    return data


class Command(BaseCommand):
    # during --help
    help = "Command to update the details of all the components from Github"

    def handle(self, *args, **options):
        all_components = get_npm_data()['objects']
        for component in all_components:
            component_data = component['package']
            try:
                _component = Component.objects.get(name=component_data['name'])
                print 'exists'
            except:
                _component = Component.objects.create(name=component_data['name'])
            print _component.name
            try:
                _component.version = component_data['version']
            except:
                pass
            try:
                _component.short_description = component_data['description']
            except:
                pass
            try:
                tags = component_data['keywords']
            except:
                tags = []
            for tag in tags:
                try:
                    _tag = Tag.objects.get(name=tag)
                except:
                    _tag = Tag.objects.create(name=tag)
                    _component.tags.add(_tag)
                if not _tag in _component.tags.all():
                    _component.tags.add(_tag)
            try:
                str_date = component_data['date']
                req_date = datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S.%fZ") #This object is timezone unaware
                aware_date = pytz.utc.localize(req_date)    #This object is now timezone aware
                _component.modified_time = aware_date
            except:
                pass
            try:
                _component.npm_url = component_data['links']['npm']
            except:
                pass
            try:
                _component.homepage_url = component_data['links']['homepage']
            except:
                pass
            try:
                github_url = component_data['links']['repository']
                url_list = github_url.split('/')
                _component.github_url = 'https://api.github.com/repos/' + str(url_list[3]) + '/' + str(url_list[4]) + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET
            except:
                pass
            try:
                _component.author = component_data['author']['name']
            except:
                pass
            try:
                _component.author_email = component_data['author']['email']
            except:
                pass
            _component.save()

            if _component.github_url:
                print _component.github_url
                github_data = get_github_data(_component.github_url)
                _component.stars = github_data['stargazers_count']
                _component.forks = github_data['forks']
                _component.watchers = github_data['watchers']
                _component.icon_url = github_data['owner']['avatar_url']
                _component.open_issues = github_data['open_issues']
                try:
                    _component.license = github_data['license']['name']
                except:
                    pass
                _component.save()
                print str(github_data['contributors_url']) + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET
                contributors_data = get_contributors_data(str(github_data['contributors_url']) + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET)
                commits = 0
                count = 0
                for contributor in contributors_data:
                    try:
                        _contributor = Contributor.objects.get(username=contributor["login"])
                    except:
                        _contributor = Contributor.objects.create(username=contributor["login"], avatar_url=contributor["avatar_url"])
                    try:
                        _contribution = Contribution.objects.get(component=_component, contributor=_contributor)
                        _contribution.contributions = contributor["contributions"]
                        _contribution.save()
                    except:
                        _contribution = Contribution.objects.create(component=_component, contributor=_contributor, contributions=contributor["contributions"])
                    commits += _contribution.contributions
                    count +=1
                _component.commits = commits
                _component.no_of_contributors = count
                _component.save()
