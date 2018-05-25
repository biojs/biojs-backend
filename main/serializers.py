from rest_framework import serializers
from .models import *

class DownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ('name', 'downloads', 'id', 'url_name')

class StarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ('name', 'stars', 'id', 'url_name')

class RecentComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ('name', 'modified_time', 'id', 'url_name')