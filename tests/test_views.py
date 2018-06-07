from django.test import TestCase

from main.models import *
from django.urls import reverse
import random
from time import sleep

class IndexViewTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Called initially when test is executed, create objects to be used by test methods
		# create 10 random objects
		number_of_components = 10
		for component_no in range(number_of_components):
			Component.objects.create(name='component'+str(component_no), downloads=random.randint(0,50), stars=random.randint(0,50))
			sleep(0.5)

	def test_view_url_exists_at_desired_location(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)

	def test_view_accessible_by_name(self):
		response = self.client.get(reverse('main:index'))
		self.assertEqual(response.status_code, 200)