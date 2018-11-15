from django.core.management import BaseCommand
import urllib2, json, urllib, base64
from main.models import *
try:
    from biojs.settings import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
except:
    print('ERROR: Could not load config!')
    GITHUB_CLIENT_ID = ''
    GITHUB_CLIENT_SECRET = ''
from datetime import datetime
import pytz
import ast
import re

# Get sniper data
'''
https://rawgit.com/cytoscape/cytoscape.js/master/package.json
"sniper" key, has "js" and "css". Search for "first"
'''

def get_npm_data():
    # response = urllib2.urlopen()
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    req = urllib2.Request("http://registry.npmjs.com/-/v1/search?text=keywords:biojs,bionode&size=500", headers=hdr)
    # req = urllib2.Request("http://registry.npmjs.com/-/v1/search?text=biojs-vis-msa&size=1", headers=hdr)
    response = urllib2.urlopen(req)
    data = json.load(response)
    return data

def send_GET_request(url, user=None, password=None):
    request = urllib2.Request(url)
    if (user is not None and password is not None):
        base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
    return urllib2.urlopen(request)

def create_jsdelivr_link(owner, repo, file_path, commit=None):
    return str('https://cdn.jsdelivr.net/gh/' + owner + '/' + repo + ('@' + commit if commit else '') + file_path)

def is_absolute_dependency(dep):
    return re.match('^(?:[a-z]+:)?//', dep) is not None

def get_owner_and_repo_from_github_url(url):
    split_url = url.split('?')[0].split('/')
    return split_url[4], split_url[5]

### store the dependency urls and snippet urls
def update_visualizations(component, commit_hash, test=False):
    owner, repo_name = get_owner_and_repo_from_github_url(component.github_url)
    try:
        url = create_jsdelivr_link(owner, repo_name, '/package.json', commit_hash)
        response = send_GET_request(url)
        package = json.load(response)
        sniper_data = package["sniper"]
    except KeyError:
        print('No sniper info in ', repo_name)
        return
    buildJS = sniper_data.get('buildJS', [])
    js = sniper_data.get('js', [])
    buildCSS = sniper_data.get('buildCSS', [])
    css = sniper_data.get('css', [])
    # Move absolute links from js to buildJS and same for css
    buildJS = buildJS + filter(lambda l: is_absolute_dependency(l), js)
    js = filter(lambda l: not is_absolute_dependency(l), js)
    buildCSS = buildCSS + filter(lambda l: is_absolute_dependency(l), css)
    css = filter(lambda l: not is_absolute_dependency(l), css)
    # Save to db
    for dep in buildJS:
        JSDependency.objects.create(component=component, js_url=dep, sniper_data_value=dep)
    for dep in buildCSS:
        CSSDependency.objects.create(component=component, css_url=dep, sniper_data_value=dep)

    sniperData, created = SniperData.objects.get_or_create(component=component)
    if 'noBrowserify' in sniper_data:
        sniperData.no_browserify = sniper_data['noBrowserify']

    sniperData.wzrd_url = '#' if sniperData.no_browserify else 'https://wzrd.in/bundle/' + component.name
    if 'snippets' in sniper_data:
        sniperData.snippets_dir_name = sniper_data['snippets'][0]
    sniperData.save()

    ### For Snippets URLs
    try:
        url = str('https://api.github.com/repos/' + owner + '/' + repo_name + '/contents/' + sniperData.snippets_dir_name + '?ref=master')
        if not test:
            print(url)
        snippets_data = send_GET_request(url, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
        snippets = json.load(snippets_data)
        filtered_snippets = filter(lambda s: s['name'].endswith('.js'), snippets)
    except Exception as e:
        print('ERROR: Something went wrong getting snipper data!')
        print(e)


    for snip in filtered_snippets:
        try:
            url = create_jsdelivr_link(owner, repo_name, str('/' + sniperData.snippets_dir_name + '/' + snip['name']), commit_hash)
            name = snip.get('name', '').split('.')[0]
            Snippet.objects.create(name=name, url=url, sniperData=sniperData)
            print('here!')
        except Exception as e:
            print('ERROR: Something went wrong creating a new Snippet')
            print(e)

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
                _component.github_url = 'https://api.github.com/repos/' + str(url_list[3]) + '/' + str(url_list[4])
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
                    response = send_GET_request(_component.github_url, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
                    github_data = json.load(response)
                except urllib2.HTTPError as e:
                    print('Error getting github data!')
                    print(e)
                    continue
                except Exception as e:
                    print('Unexpected error accessing Github!')
                    print(e)
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
                    response = send_GET_request(github_data['commits_url'].split('{')[0], GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
                    latest_commit = json.load(response)[0]
                    latest_commit_hash = latest_commit['sha']
                    _component.latest_commit_hash = latest_commit_hash
                except:
                    print('Error getting commit hash!')
                    pass
                try:
                    update_visualizations(_component, latest_commit_hash)
                except Exception as e:
                    print('Error updating visualisations!')
                    print(e)
                # except:
                #     pass
                _component.save()
                print (str(github_data['contributors_url']))
                try:
                    response = send_GET_request(str(github_data['contributors_url']), GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
                    contributors_data = json.load(response)
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
                    print ('Error')
                    continue
                response = send_GET_request(github_data['downloads_url'], GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
                downloads_array = json.load(response)
                _component.downloads = len(downloads_array)
                _component.commits = commits
                _component.no_of_contributors = count
                _component.save()
