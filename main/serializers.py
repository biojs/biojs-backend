from rest_framework import serializers
from .models import *

class DownloadSerializer(serializers.ModelSerializer):
    property = serializers.SerializerMethodField()

    def get_property(self, component):
        return component.downloads

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