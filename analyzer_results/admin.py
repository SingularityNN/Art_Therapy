from django.contrib import admin

from .models import Experiments


@admin.register(Experiments)
class ExperimentsAdmin(admin.ModelAdmin):
    list_display = "id", "drawing", "psych_test_image"

