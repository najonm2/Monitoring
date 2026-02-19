from django.db import models


class Application(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class Report(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="reports")
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.CharField(max_length=500, blank=True)
    ssrs_url = models.CharField(max_length=1000)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["display_order", "name"]
        unique_together = ("application", "slug")

    def __str__(self):
        return f"{self.application.name} - {self.name}"