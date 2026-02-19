from django.contrib import admin
from .models import Application, Report


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "application", "slug", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    list_filter = ("application", "is_active")
    search_fields = ("name", "slug", "application__name")
    prepopulated_fields = {"slug": ("name",)}