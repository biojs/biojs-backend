from rest_framework import serializers
from .models import *

class DownloadSerializer(serializers.ModelSerializer):
    property = serializers.SerializerMethodField()

    def get_property(self, component):
        return component.forks

    class Meta:
        model = Component
        fields = ('name', 'property', 'id', 'url_name')

class StarSerializer(serializers.ModelSerializer):
    property = serializers.SerializerMethodField()

    def get_property(self, component):
        return component.stars

    class Meta:
        model = Component
        fields = ('name', 'property', 'id', 'url_name')

class RecentComponentSerializer(serializers.ModelSerializer):
    property = serializers.SerializerMethodField()

    def get_property(self, component):
        return component.modified_time

    class Meta:
        model = Component
        fields = ('name', 'property', 'id', 'url_name')

class TopComponentSerializer(serializers.ModelSerializer):  # Data fields when viewing the overall top components
    tags = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()
    def get_tags(self, obj):
        tags = []
        for t in obj.tags.all():
            tags.append(t.name)
        return tags
    def get_icon_url(self, obj):
        if obj.icon:
            request = self.context.get('request')
            icon_url =  obj.icon.url
            return request.build_absolute_uri(icon_url)
        else:
            return '#'
    class Meta:
        model = Component
        fields = ('name', 'tags', 'icon_url', 'downloads', 'stars', 'modified_time', 'short_description', 'id', 'url_name', 'author')

class DetailComponentSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()
    def get_tags(self, obj):
        tags = []
        for t in obj.tags.all():
            tags.append(t.name)
        return tags
    def get_icon_url(self, obj):
        if obj.icon:
            request = self.context.get('request')
            icon_url =  obj.icon.url
            return request.build_absolute_uri(icon_url)
        else:
            return '#'
    class Meta:
        model = Component
        fields = (
                'name',
                'stars',
                'downloads',
                'modified_time',
                'tags',
                'icon_url',
                'github_url',
                'short_description',
                'url_name',
                'commits',
                'forks',
                'watchers',
                'no_of_contributors',
                'version',
                'author',
                'author_email',
                'npm_url',
                'homepage_url',
                'license',
            )

class BaseComponentSerializer(serializers.ModelSerializer): #serializer fields used while querying
    tags = serializers.SerializerMethodField()
    def get_tags(self, obj):
        tags = []
        for t in obj.tags.all():
            tags.append(t.name)
        return tags
    class Meta:
        model = Component
        fields = ('name', 'tags', 'id', 'url_name')

class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ('username', 'avatar_url')

class ContributionSerializer(serializers.ModelSerializer):
    contributor = ContributorSerializer(required=True, write_only=True)

    class Meta:
        model = Contribution
        fields = ('contributor', 'contributions')