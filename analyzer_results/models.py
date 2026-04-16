from django.db import models

class Experiments(models.Model):
    id = models.CharField(null=False, primary_key=True, max_length=100)
    drawing_first = models.ImageField()
    analyzer_res_first_json = models.JSONField(default=dict, blank=True)
    drawing_second = models.ImageField()
    analyzer_res_second_json = models.JSONField(default=dict, blank=True)
    note = models.TextField(default="", blank=True)

    def __str__(self) -> str:
        return self.id

    class Meta:
        ordering = ["id", ]
        verbose_name_plural = "Experiments"