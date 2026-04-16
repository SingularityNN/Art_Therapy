from django.contrib import admin

from .models import Experiments


@admin.register(Experiments)
class ExperimentsAdmin(admin.ModelAdmin):
    list_display = ("display_id", "drawing_first", "drawing_second")

    list_display_links = ("display_id",)

    @admin.display(description="ID")  # Заголовок колонки
    def display_id(self, obj):
        # Возвращаем СЫРОЕ значение id из базы,
        # Django сам подтянет логику отображения
        return obj.id


