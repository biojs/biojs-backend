from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.files import File
import requests, os, urllib
from urlparse import urlparse
import urllib2
from django.core.files.base import ContentFile

def get_remote_image(self):
    if self.icon_url and not self.icon:
        result = urllib.urlretrieve(self.icon_url)
        self.icon.save(
                os.path.basename(self.icon_url),
                File(open(result[0]))
                )
        self.save()

class Component(models.Model):
    name = models.CharField(max_length=100)
    stars = models.IntegerField(default=0, null=True)
    downloads = models.BigIntegerField(default=0, null=True)
    created_time = models.DateTimeField(null=True)
    modified_time = models.DateTimeField(null=True)
    tags = models.ManyToManyField('Tag')
    icon_url = models.URLField(null=True, blank=True)
    icon = models.ImageField(null=True, upload_to='icons/')
    github_url = models.URLField(null=True)
    short_description = models.TextField(null=True)
    url_name = models.SlugField(null=True, unique=True, max_length=255)
    commits = models.IntegerField(default=0, null=True)
    forks = models.IntegerField(default=0, null=True)
    watchers = models.IntegerField(default=0, null=True)
    no_of_contributors = models.IntegerField(default=0, null=True)
    version = models.CharField(max_length=100, null=True)
    no_of_releases = models.IntegerField(default=0)
    open_issues = models.IntegerField(default=0)
    author = models.CharField(max_length=200, null=True)
    author_email = models.EmailField(null=True)
    npm_url = models.URLField(null=True)
    homepage_url = models.URLField(null=True)
    license = models.CharField(max_length=100, null=True)
    github_update_time = models.DateTimeField(null=True)
    latest_commit_hash = models.CharField(max_length=40, null=True)

    def save(self, *args, **kwargs):
        if not self.url_name:
            self.url_name = (str(self.name).replace(' ', '-')).replace('/', '-').replace('@','').replace('.', '-').lower()
        return super(Component, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Contributor(models.Model):
    username = models.CharField(max_length=100)
    avatar_url = models.URLField()
    components = models.ManyToManyField(Component, through="Contribution")

    def __unicode__(self):
        return self.username

class Contribution(models.Model):
    contributor = models.ForeignKey(Contributor, on_delete=models.SET_NULL, null=True)
    component = models.ForeignKey(Component, on_delete=models.SET_NULL, null=True, related_name='contributions')
    contributions = models.IntegerField(default=0)

class Visualization(models.Model):
    name = models.CharField(max_length=100)
    component = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL)
    url = models.URLField(null=True)

    def __unicode__(self):
        return self.name + '-' + str(self.component.name)

class JSDependency(models.Model):
    js_url = models.URLField(null=True)
    component = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL)
    sniper_data_value = models.CharField(max_length=500, null=True)

    def __unicode__(self):
        return str(self.component)

class CSSDependency(models.Model):
    css_url = models.URLField(null=True)
    component = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL)
    sniper_data_value = models.CharField(max_length=500, null=True)

    def __unicode__(self):
        return str(self.component)

class SniperData(models.Model):
    no_browserify = models.BooleanField(default=False)
    wzrd_url = models.URLField(null=True)
    component = models.OneToOneField(Component, on_delete=models.SET_NULL, null=True)
    snippets_dir_name = models.CharField(max_length=100, default='snippets')

    def __unicode__(self):
        return str(self.component)

class Snippet(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=100)
    sniperData = models.ForeignKey(SniperData, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return str(self.sniperData.component)