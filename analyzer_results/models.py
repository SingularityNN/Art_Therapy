from django.db import models

class Experiments(models.Model):
    id = models.CharField(null=False, primary_key=True, max_length=100)
    drawing = models.ImageField()
    analyzer_res_json = models.JSONField(default=dict, blank=True)
    psych_test_image = models.ImageField()
    psych_test_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id", ]