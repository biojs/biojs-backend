from django.test import TestCase

# Tests for models

from main.models import *
import re

class ComponentModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Called initially when test is executed, create object to be used by test methods
		Component.objects.create(name='@test/component', author='test_author')

	# Test max length of name
	def test_name_max_length(self):
		component = Component.objects.get(id=1)
		max_length = component._meta.get_field('name').max_length
		self.assertEquals(max_length, 100)

	# Test if url_name is a Slug Field
	def test_url_name(self):
		component = Component.objects.get(id=1)
		url_name = component.url_name
		self.assertTrue(re.match('[-\w]+', url_name))

	# Test max length of author name
	def test_author_max_length(self):
		component = Component.objects.get(id=1)
		max_length = component._meta.get_field('author').max_length
		self.assertEquals(max_length, 200)

class TagModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Called initially when test is executed, create object to be used by test methods
		Tag.objects.create(name='test_tag')

	# Test max length of name
	def test_name_max_length(self):
		tag = Tag.objects.get(id=1)
		max_length = tag._meta.get_field('name').max_length
		self.assertEquals(max_length, 50)

class ContributorModelTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		# Called initially when test is executed, create object to be used by test methods
		Contributor.objects.create(username='test_contributor')

	# Test max length of name
	def test_name_max_length(self):
		contributor = Contributor.objects.get(id=1)
		max_length = contributor._meta.get_field('username').max_length
		self.assertEquals(max_length, 100)