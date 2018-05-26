from django.core.management import BaseCommand
import urllib, json
from main.models import *

def get_json_data(github_url):
    response = urllib.urlopen(github_url)
    data = json.loads(response.read())
    return data

class Command(BaseCommand):
    # during --help
    help = "Command to update the details of all the components from Github"

    def handle(self, *args, **options):
        for component in Component.objects.all():
            self.stdout.write(component.name) #testing
            # try:
            #     component_data = get_json_data(component.github_url)
            #     component.stars = component_data['stargazers_count']
            #     component.save()
            # except:
            #     continue