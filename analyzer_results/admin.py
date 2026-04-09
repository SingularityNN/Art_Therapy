from django.contrib import admin

from analyzer_results.models import Experiments


@admin.register(Experiments)
class ExperimentsAdmin(admin.ModelAdmin):
    pass

