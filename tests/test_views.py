from django.test import TestCase

from main.models import *
from django.urls import reverse
import random
from time import sleep
from datetime import datetime
import pytz
import urllib, urllib2
import json
import ast
from main.management.commands import updatecomponents
try:
	from biojs.config import *
except:
	GITHUB_CLIENT_ID = ''
	GITHUB_CLIENT_SECRET = ''

class IndexViewTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Called initially when test is executed, create objects to be used by test methods
		# create 10 random objects
		number_of_components = 10
		for component_no in range(number_of_components):
			Component.objects.create(name='component'+str(component_no), downloads=random.randint(0,50), stars=random.randint(0,50), modified_time=pytz.utc.localize(datetime.now()))
			# sleep(0.5)

	def test_view_url_exists_at_desired_location(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)

	def test_view_accessible_by_name(self):
		response = self.client.get(reverse('main:index'))
		self.assertEqual(response.status_code, 200)

	# Tests whether the relevant keys are present in the json response and length of each list is maximum 3
	def test_relevance_of_response(self):
		response = self.client.get(reverse('main:index'))
		self.assertTrue('most_recent_components' in response.json())
		self.assertTrue('top_dl_components' in response.json())
		self.assertTrue('top_starred_components' in response.json())
		self.assertTrue(len(response.json()['most_recent_components'])<4)
		self.assertTrue(len(response.json()['top_dl_components'])<4)
		self.assertTrue(len(response.json()['top_starred_components'])<4)
		# Test if all the required fields are present in the response
		for object in response.json()['most_recent_components']:
			self.assertTrue('name' in object and 
							'property' in object and
							'id' in object and
							'url_name' in object
						)

		for object in response.json()['top_dl_components']:
			self.assertTrue('name' in object and 
							'property' in object and
							'id' in object and
							'url_name' in object
						)

		for object in response.json()['top_starred_components']:
			self.assertTrue('name' in object and
							'property' in object and
							'id' in object and
							'url_name' in object
						)

class TopComponentViewTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Called initially when test is executed, create objects to be used by test methods
		# create 10 random objects
		number_of_components = 20
		for component_no in range(number_of_components):
			Component.objects.create(name='component'+str(component_no), downloads=random.randint(0,50), stars=random.randint(0,50), modified_time=pytz.utc.localize(datetime.now()))
			# sleep(0.5)

	def test_view_url_exists_at_desired_location(self):
		response = self.client.get('/top/')
		self.assertEqual(response.status_code, 200)

	def test_view_accessible_by_name(self):
		response = self.client.get(reverse('main:top_components'))
		self.assertEqual(response.status_code, 200)

	# Tests whether the relevant keys are present in the json response and length of each list is maximum 10
	def test_relevance_of_response(self):
		response = self.client.get(reverse('main:top_components'))
		self.assertTrue('top_components' in response.json())
		self.assertTrue(len(response.json()['top_components'])<11)
		# Test if all the required fields are present in the response
		for object in response.json()['top_components']:
			self.assertTrue(
					'name' in object and
					'tags' in object and
					'icon_url' in object and
					'downloads' in object and
					'stars' in object and
					'modified_time' in object and
					'short_description' in object and
					'id' in object and
					'url_name' in object and
					'author' in object
				)

class AllComponentViewTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Called initially when test is executed, create objects to be used by test methods
		# create 20 random objects
		number_of_components = 20
		for component_no in range(number_of_components):
			Component.objects.create(name='component'+str(component_no), downloads=random.randint(0,50), stars=random.randint(0,50), modified_time=pytz.utc.localize(datetime.now()))
			# sleep(0.5)

	def test_view_url_exists_at_desired_location(self):
		response = self.client.get('/all/')
		self.assertEqual(response.status_code, 200)

	def test_view_accessible_by_name(self):
		response = self.client.get(reverse('main:all_components'))
		self.assertEqual(response.status_code, 200)

	# Tests whether the relevant keys are present in the json response and length of response list is same as number of components in database
	def test_relevance_of_response(self):
		response = self.client.get(reverse('main:all_components'))
		self.assertTrue('all_components' in response.json())
		self.assertEqual(len(response.json()['all_components']), Component.objects.all().count())
		# Test if all the required fields are present in the response
		for object in response.json()['all_components']:
			self.assertTrue(
					'name' in object and
					'tags' in object and
					'id' in object and
					'url_name' in object
				)

class DetailComponentViewTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Called initially when test is executed, create objects to be used by test methods
		# create a random object
		# Add a benchmark component
		hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
		req = urllib2.Request("http://registry.npmjs.com/-/v1/search?text=biojs-vis-rohart-msc-test", headers=hdr)
		response = urllib2.urlopen(req)
		data = json.load(response)
		hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
		req = urllib2.Request("http://registry.npmjs.com/-/v1/search?text=cytoscape&size=1", headers=hdr)
		response = urllib2.urlopen(req)
		data['objects'].append(json.load(response)['objects'][0])
		### BENCHMARK COMPONENT
		hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
		req = urllib2.Request("http://registry.npmjs.com/-/v1/search?text=gmkhsuorlom4n85u&size=1", headers=hdr)
		response = urllib2.urlopen(req)
		data['objects'].append(json.load(response)['objects'][0])
		for component in data['objects']:
			component_data = component['package']
			_component = Component.objects.create(name=component_data['name'])
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
				# print _component.github_url
				response = urllib.urlopen(_component.github_url)
				github_data = json.load(response)
				_component.stars = github_data['stargazers_count']
				_component.forks = github_data['forks']
				_component.watchers = github_data['watchers']
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
				str_date = github_data['updated_at']
				req_date = datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%SZ")
				aware_date = pytz.utc.localize(req_date)
				_component.github_update_time = aware_date
				commits_url = github_data['commits_url'].split('{')[0] + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET
				response = urllib.urlopen(commits_url)
				data = json.loads(response.read())[0]
				_component.latest_commit_hash = data['sha']
				_component.save()
				updatecomponents.update_visualizations(_component, _component.latest_commit_hash, True)
				contributors_data = json.load(urllib.urlopen(str(github_data['contributors_url'] + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET)))
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
				response = urllib.urlopen(github_data['downloads_url'] + '?client_id=' + GITHUB_CLIENT_ID + '&client_secret=' + GITHUB_CLIENT_SECRET)
				downloads = 0
				data = ast.literal_eval(response.read())
				for download in data:
				    downloads += int(download['download_count'])
				_component.downloads = downloads
				_component.commits = commits
				_component.no_of_contributors = count
				_component.save()

	def test_view_url_exists_at_desired_location(self):
		response = self.client.get('/details/biojs-vis-rohart-msc-test/')
		self.assertEqual(response.status_code, 200)
		response = self.client.get('/details/cytoscape/')
		self.assertEqual(response.status_code, 200)
		response = self.client.get('/details/mplexviz-ngraph/')
		self.assertEqual(response.status_code, 200)

	def test_view_accessible_by_name(self):
		response = self.client.get(reverse('main:component_details', kwargs={'url_name':'biojs-vis-rohart-msc-test'}))
		self.assertEqual(response.status_code, 200)
		response = self.client.get(reverse('main:component_details', kwargs={'url_name':'cytoscape'}))
		self.assertEqual(response.status_code, 200)
		response = self.client.get(reverse('main:component_details', kwargs={'url_name':'mplexviz-ngraph'}))
		self.assertEqual(response.status_code, 200)

	# Tests whether the relevant keys are present in the json response and length of response list is same as number of components in database
	def test_relevance_of_response(self):
		# call for biojs-vis-rohart-msc-test
		response_1 = self.client.get(reverse('main:component_details', kwargs={'url_name':'biojs-vis-rohart-msc-test'}))
		self.assertTrue('details' in response_1.json())
		objects = []
		objects.append(response_1.json()['details'])
		# call for cytoscape
		response_2 = self.client.get(reverse('main:component_details', kwargs={'url_name':'cytoscape'}))
		self.assertTrue('details' in response_2.json())
		objects.append(response_2.json()['details'])
		# call for mplexviz-ngraph
		response_3 = self.client.get(reverse('main:component_details', kwargs={'url_name':'mplexviz-ngraph'}))
		self.assertTrue('details' in response_3.json())
		objects.append(response_3.json()['details'])
		# Test if all the required fields are present in the response
		for object in objects:
			self.assertTrue(
					'name' in object and
					'tags' in object and
					'stars' in object and
					'downloads' in object and
					'created_time' in object and
					'modified_time' in object and
					'icon_url' in object and
					'github_url' in object and
					'short_description' in object and
					'url_name' in object and
					'commits' in object and
					'forks' in object and
					'watchers' in object and
					'no_of_contributors' in object and
					'open_issues' in object and
					'version' in object and
					'author' in object and
					'license' in object and
					'github_update_time' in object and
					'latest_commit_hash' in object
				)
		# check if number of commits >= 50 for biojs-vis-rohart-msc-test 
		# and >= 3757 for cytoscape, from the time the tests were initiated
		### As number of stars, watchers might go down in the future so they haven't been tested
		self.assertTrue(int(response_1.json()['details']['commits']) >= 50)
		self.assertTrue(int(response_2.json()['details']['commits']) >= 3757)

		# Tests for benchmark component
		self.assertTrue(int(response_3.json()['details']['stars']) >= 3)
		self.assertTrue(int(response_2.json()['details']['commits']) >= 70)

		# modified date should be after created date
		self.assertTrue(response_1.json()['details']['created_time'] <= response_1.json()['details']['github_update_time']) # for biojs-vis-rohart-msc-test
		self.assertTrue(response_2.json()['details']['created_time'] <= response_2.json()['details']['github_update_time']) # for cytoscape
		self.assertTrue(response_3.json()['details']['created_time'] <= response_3.json()['details']['github_update_time']) # for mplexviz-ngraph
		# check if number of contributors is same as contributors added
		self.assertEqual(response_1.json()['details']['no_of_contributors'], Contribution.objects.filter(component=Component.objects.get(name='biojs-vis-rohart-msc-test')).count())
		self.assertEqual(response_1.json()['details']['no_of_contributors'], len(response_1.json()['contributors']))
		self.assertEqual(response_2.json()['details']['no_of_contributors'], Contribution.objects.filter(component=Component.objects.get(name='cytoscape')).count())
		self.assertEqual(response_2.json()['details']['no_of_contributors'], len(response_2.json()['contributors']))
		self.assertEqual(response_3.json()['details']['no_of_contributors'], Contribution.objects.filter(component=Component.objects.get(name='mplexviz-ngraph')).count())
		self.assertEqual(response_3.json()['details']['no_of_contributors'], len(response_3.json()['contributors']))
		for object in response_1.json()['contributors'] + response_2.json()['contributors'] + response_3.json()['contributors']:
			self.assertTrue(
					'contributor' in object and
					'contributions' in object and
					'id' in object
				)
			contributor_details = object['contributor']
			self.assertTrue(
					'username' in contributor_details and
					'avatar_url' in contributor_details
				)

		# tests for visualizations
		# Test for JS and CSS dependencies as well as snippets names.
		# Cytoscape
		if 'js_dependencies' in response_2.json():
			for js_dependency in response_2.json()['js_dependencies']:
				url = js_dependency['js_url']
				latest_commit_hash = response_2.json()['details']['latest_commit_hash']
				# Verify that cdn URL is configured correctly
				if('cdn.rawgit.com' in url):
					self.assertTrue(latest_commit_hash in url)
		if 'css_dependencies' in response_2.json():
			for css_dependency in response_2.json()['css_dependencies']:
				url = css_dependency['css_url']
				latest_commit_hash = response_2.json()['details']['latest_commit_hash']
				# Verify that cdn URL is configured correctly
				if('cdn.rawgit.com' in url):
					self.assertTrue(latest_commit_hash in url)
		if 'snippets' in response_2.json():
			snippets_list = ['animated-bfs', 'images', 'performance-tuning', 'visual']
			for snippet in response_2.json()['snippets']:
				latest_commit_hash = response_2.json()['details']['latest_commit_hash']
				url = snippet['url']
				name = snippet['name']
				if('cdn.rawgit.com' in url):
					self.assertTrue(latest_commit_hash in url)
				self.assertTrue(name in snippets_list)

		# mplexviz-ngraph
		if 'js_dependencies' in response_3.json():
			for js_dependency in response_3.json()['js_dependencies']:
				url = js_dependency['js_url']
				latest_commit_hash = response_3.json()['details']['latest_commit_hash']
				# Verify that cdn URL is configured correctly
				if('cdn.rawgit.com' in url):
					self.assertTrue(latest_commit_hash in url)
		if 'css_dependencies' in response_3.json():
			for css_dependency in response_3.json()['css_dependencies']:
				url = css_dependency['css_url']
				latest_commit_hash = response_3.json()['details']['latest_commit_hash']
				# Verify that cdn URL is configured correctly
				if('cdn.rawgit.com' in url):
					self.assertTrue(latest_commit_hash in url)
		if 'snippets' in response_3.json():
			snippets_list = ['one', 'two', 'three']
			for snippet in response_3.json()['snippets']:
				latest_commit_hash = response_3.json()['details']['latest_commit_hash']
				url = snippet['url']
				name = snippet['name']
				if('cdn.rawgit.com' in url):
					self.assertTrue(latest_commit_hash in url)
				self.assertTrue(name in snippets_list)
