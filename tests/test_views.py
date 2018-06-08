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
			sleep(0.5)

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