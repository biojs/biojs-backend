from django.core.management import BaseCommand
import urllib, json
from main.models import *
from biojs.config import *

def get_github_data(github_url):
    response = urllib.urlopen(github_url)       # 'https://api.github.com/users/whatever?client_id=xxxx&client_secret=yyyy' format
    data = json.loads(response.read())
    return data

def get_npm_data():
    response = urllib.urlopen("https://api.npms.io/v2/search?q=keywords:biojs")
    data = json.loads(response.read())
    return data

def get_contributors_data(contributors_url):
    response = urllib.urlopen(contributors_url)
    data = json.loads(response.read())
    return data


class Command(BaseCommand):
    # during --help
    help = "Command to update the details of all the components from Github"

    def handle(self, *args, **options):
        all_components = get_npm_data()['results']
        for component in all_components:
            component_data = component['package']
            try:
                _component = Component.objects.get(name=component_data['name'])
            except:
                _component = Component.objects.create(name=component_data['name'])
            _component.version = component_data['version']
            _component.short_description = component_data['description']
            tags = component_data['keywords']
            for tag in tags:
                try:
                    _tag = Tag.objects.get(name=tag)
                    if not _tag in _component.tags:
                        _component.tags.add(_tag)
                except:
                    _tag = Tag.objects.create(name=tag)
                    _component.tags.add(_tag)
            ### Add date after parsing
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
                contributors_data = get_contributors_data(github_data['contributors_url'])
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
