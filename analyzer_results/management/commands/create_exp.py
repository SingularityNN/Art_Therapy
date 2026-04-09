from django.core.management import BaseCommand
from analyzer_results.models import Experiments


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Creating new entity")

        experiment, created = Experiments.objects.get_or_create(id='art/image1.jpg')
        if created:
            self.stdout.write(self.style.SUCCESS(f"SUCCESS, id: {experiment.id}"))