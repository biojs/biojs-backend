from django.test import TestCase

from main.models import *
from django.urls import reverse
import random
from time import sleep
from datetime import datetime
import pytz

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
		component = Component.objects.create(
				name = "testComponent",
				stars = random.randint(0, 20),
				downloads = random.randint(0, 20),
				created_time = pytz.utc.localize(datetime.now()),
				modified_time = pytz.utc.localize(datetime.now()),
				no_of_contributors = 2,
				license = 'MIT'
			)
		contributor1 = Contributor.objects.create(
				username = "contributor1",
				avatar_url = "https://avatars1.githubusercontent.com/u/11511612?v=4"
			)
		contributions1 = random.randint(0,100)
		Contribution.objects.create(contributor=contributor1, component=component, contributions=contributions1)
		contributor2 = Contributor.objects.create(
				username = "contributor2",
				avatar_url = "https://avatars1.githubusercontent.com/u/11511612?v=4"
			)
		contributions2 = random.randint(0,100)
		Contribution.objects.create(contributor=contributor2, component=component, contributions=contributions2)
		component.commits = contributions1 + contributions2
		component.save()

	def test_view_url_exists_at_desired_location(self):
		response = self.client.get('/details/testcomponent/')
		self.assertEqual(response.status_code, 200)

	def test_view_accessible_by_name(self):
		response = self.client.get(reverse('main:component_details', kwargs={'url_name':'testcomponent'}))
		self.assertEqual(response.status_code, 200)

	# Tests whether the relevant keys are present in the json response and length of response list is same as number of components in database
	def test_relevance_of_response(self):
		response = self.client.get(reverse('main:component_details', kwargs={'url_name':'testcomponent'}))
		self.assertTrue('details' in response.json())
		# Test if all the required fields are present in the response
		object = response.json()['details']
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
				'license' in object
			)
		# check if number of contributors is same as contributors added
		self.assertEqual(response.json()['details']['no_of_contributors'], Contribution.objects.filter(component=Component.objects.get(name='testComponent')).count())
		self.assertEqual(response.json()['details']['no_of_contributors'], len(response.json()['contributors']))
		for object in response.json()['contributors']:
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
