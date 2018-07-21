from django.core.management import BaseCommand
import urllib2, json, urllib
from main.models import *
try:
    from biojs.config import *
except:
    GITHUB_CLIENT_ID = ''
    GITHUB_CLIENT_SECRET = ''
from datetime import datetime
import pytz
import ast

# Get sniper data
'''
https://rawgit.com/cytoscape/cytoscape.js/master/package.json
"sniper" key, has "js" and "css". Search for "first"
'''

def get_commit_hash(commits_url):
    commits_url = commits_url.split('{')[0] + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET
    print (commits_url)
    response = urllib.urlopen(commits_url)
    data = json.loads(response.read())[0]
    return data['sha']

### store the dependency urls and snippet urls
def update_visualizations(component, commit_hash, test=False):
    github_url_list = component.github_url.split('?')[0].split('/')
    owner = github_url_list[4]
    repo_name = github_url_list[5]
    try:
        sniper_data = json.load(urllib.urlopen("https://cdn.rawgit.com/" + str(owner) + 
                                '/' + str(repo_name) + "/" + commit_hash + "/package.json"))["sniper"]
    except:
        return
    try:
        buildJS = sniper_data["buildJS"]
    except:
        buildJS = []
    try:
        js = sniper_data["js"]
    except:
        js = []
    js_dependencies = buildJS + js
    try:
        buildCSS = sniper_data["buildCSS"]
    except:
        buildCSS = []
    try:
        css = sniper_data["css"]
    except:
        css = []
    css_dependencies = buildCSS + css
    for dependency in js_dependencies:
        if dependency.startswith('http') :
            dependency, created = JSDependency.objects.get_or_create(component=component, js_url=dependency)
        elif dependency.startswith('/'):
            dependency_string = dependency
            if 'build/' in dependency_string:
                continue
            dependency = "https://cdn.rawgit.com/" + str(owner) + '/' + str(repo_name) + "/" + commit_hash + dependency
            try:
                req_dependency = JSDependency.objects.get(component=component, sniper_data_value=dependency_string)
                req_dependency.js_url = dependency
                req_dependency.save()
            except:
                req_dependency = JSDependency.objects.create(component=component, sniper_data_value=dependency_string, js_url=dependency)
        else:
            dependency_string = dependency
            if 'build/' in dependency_string:
                continue
            dependency = "https://cdn.rawgit.com/" + str(owner) + '/' + str(repo_name) + "/" + commit_hash + "/" + dependency
            try:
                req_dependency = JSDependency.objects.get(component=component, sniper_data_value=dependency_string)
                req_dependency.js_url = dependency
                req_dependency.save()
            except:
                req_dependency = JSDependency.objects.create(component=component, sniper_data_value=dependency_string, js_url=dependency)
    for dependency in css_dependencies:
        if dependency.startswith('http'):
            dependency, created = CSSDependency.objects.get_or_create(component=component, css_url=dependency)
        elif dependency.startswith('/'):
            dependency_string = dependency
            if 'build/' in dependency_string:
                continue
            dependency = "https://cdn.rawgit.com/" + str(owner) + '/' + str(repo_name) + "/" + commit_hash + dependency
            try:
                req_dependency = CSSDependency.objects.get(component=component, sniper_data_value=dependency_string)
                req_dependency.css_url = dependency
                req_dependency.save()
            except:
                req_dependency = CSSDependency.objects.create(component=component, sniper_data_value=dependency_string, css_url=dependency)
        else:
            dependency_string = dependency
            if 'build/' in dependency_string:
                continue
            dependency = "https://cdn.rawgit.com/" + str(owner) + '/' + str(repo_name) + "/" + commit_hash + dependency
            try:
                req_dependency = CSSDependency.objects.get(component=component, sniper_data_value=dependency_string)
                req_dependency.css_url = dependency
                req_dependency.save()
            except:
                req_dependency = CSSDependency.objects.create(component=component, sniper_data_value=dependency_string, css_url=dependency)
    try:
        sniperData = SniperData.objects.get(component=component)
    except:
        sniperData = SniperData.objects.create(component=component)
    try:
        no_browserify = sniper_data['noBrowserify']
        sniperData.no_browserify = no_browserify
    except:
        pass
    try:
        if no_browserify:
            sniperData.wzrd_url = '#'
        else:
            sniperData.wzrd_url = "https://wzrd.in/bundle/" + component.name    
    except:
        sniperData.wzrd_url = "https://wzrd.in/bundle/" + component.name
    try:
        snippets_dir_name = sniper_data['snippets'][0]
        sniperData.snippets_dir_name = snippets_dir_name
    except:
        pass
    sniperData.save()

    ### For Snippets URLs
    try:
        if not test:
            print ("https://api.github.com/repos/" + str(owner) + "/" + str(repo_name) + "/contents/" + sniperData.snippets_dir_name + "?ref=master&client_id="
                                            + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_CLIENT_SECRET)
        snippets_data = urllib.urlopen("https://api.github.com/repos/" + str(owner) + "/" + str(repo_name) + "/contents/" + sniperData.snippets_dir_name + "?ref=master&client_id="
                                            + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_CLIENT_SECRET)
        snippets = json.loads(snippets_data.read())
        for snippet in snippets:
            if not snippet['name'].endswith('.js'):
                continue
            url = "https://cdn.rawgit.com/" + str(owner) + '/' + str(repo_name) + "/" + commit_hash + "/" + sniperData.snippets_dir_name + "/" + snippet['name']
            try:
                name = snippet['name'].split('.')[0]
                req_snippet = Snippet.objects.get(name=name, sniperData=sniperData)
                req_snippet.url = url
                req_snippet.save()
            except:
                name = snippet['name'].split('.')[0]
                Snippet.objects.create(name=name, sniperData=sniperData, url=url)
    except:
        pass

def get_github_data(github_url):
    response = urllib.urlopen(github_url)
    data = json.load(response)
    return data

def get_npm_data():
    # response = urllib2.urlopen()
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    req = urllib2.Request("http://registry.npmjs.com/-/v1/search?text=keywords:biojs,bionode&size=500", headers=hdr)
    # req = urllib2.Request("http://registry.npmjs.com/-/v1/search?text=biojs-vis-msa&size=1", headers=hdr)
    response = urllib2.urlopen(req)
    data = json.load(response)
    return data

def get_contributors_data(contributors_url):
    response = urllib.urlopen(contributors_url)
    data = json.load(response)
    return data

def get_downloads(downloads_url):
    print (downloads_url)
    response = urllib.urlopen(downloads_url)
    downloads = 0
    data = ast.literal_eval(response.read())
    for download in data:
        downloads += int(download['download_count'])
    return downloads


class Command(BaseCommand):
    # during --help
    help = "Command to update the details of all the components from Github"

    def handle(self, *args, **options):
        all_components = get_npm_data()['objects']
        for component in all_components:
            component_data = component['package']
            try:
                _component = Component.objects.get(name=component_data['name'])
                print ('exists')
            except:
                _component = Component.objects.create(name=component_data['name'])
            print (_component.name)
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
                print (_component.github_url)
                try:
                    github_data = get_github_data(_component.github_url)
                except:
                    continue
                _component.stars = github_data['stargazers_count']
                _component.forks = github_data['forks']
                # subscriber_count
                _component.watchers = github_data['subscribers_count']
                _component.icon_url = github_data['owner']['avatar_url']
                _component.open_issues = github_data['open_issues']
                try:
                    _component.license = github_data['license']['name']
                except:
                    pass
                try:
                    str_date = github_data['created_at']
                    req_date = datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%SZ") #This object is timezone unaware
                    aware_date = pytz.utc.localize(req_date)    #This object is now timezone aware
                    _component.created_time = aware_date
                except:
                    pass
                # try:
                str_date = github_data['updated_at']
                req_date = datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%SZ") #This object is timezone unaware
                aware_date = pytz.utc.localize(req_date)    #This object is now timezone aware
                # if _component.github_update_time:
                #     if aware_date > _component.github_update_time:
                #         _component.github_updated_time = aware_date
                #         latest_commit_hash = get_commit_hash(github_data['commits_url'])
                #         _component.latest_commit_hash = latest_commit_hash
                        # update_visualizations(_component, latest_commit_hash)
                # else:
                _component.github_update_time = aware_date
                try:
                    latest_commit_hash = get_commit_hash(github_data['commits_url'])
                except:
                    continue
                _component.latest_commit_hash = latest_commit_hash
                update_visualizations(_component, latest_commit_hash)
                # except:
                #     pass
                _component.save()
                print (str(github_data['contributors_url']) + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET)
                try:
                    contributors_data = get_contributors_data(str(github_data['contributors_url']) + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET)
                except:
                    continue
                commits = 0
                count = 0
                try:
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
                except:
                    print 'Error'
                    continue
                try:
                    _component.downloads = get_downloads(str(github_data['downloads_url']) + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET)
                except:
                    pass
                _component.commits = commits
                _component.no_of_contributors = count
                _component.save()
