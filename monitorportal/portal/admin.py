from django.contrib import admin
from .models import Application, Report, ERPRunRecovery


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "display_order"]
    list_editable = ["is_active", "display_order"]  
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("name", "application", "slug", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    list_filter = ("application", "is_active")
    search_fields = ("name", "slug", "application__name")
    prepopulated_fields = {"slug": ("name",)}

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if response.context_data.get('cl'):
            response.context_data['cl'].data = response.context_data['cl'].queryset
        return response

    def get_view_type(self, obj):
        # This method maps the report name to the view_type
        view_type_mapping = {
            "lvl3-failed-job-status": "level3_failed",
            "lvl3-failed-with-error": "level3_error",
            "lvl3-long-running-sessions": "level3_long_running",
            "mdm-job-status": "mdm_job_status",
            "erp-job-status-latest": "erp_job_status",
        }
        return view_type_mapping.get(obj.name, "")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Here you can add any custom filtering logic if needed
        return qs

    def level3_failed_job_status(self, request, *args, **kwargs):
        # Custom view logic for level3 failed job status
        return self.render_to_response(
            self.get_context_data(
                object_list=self.get_queryset(request).filter(name="lvl3-failed-job-status")
            )
        )


@admin.register(ERPRunRecovery)
class ERPRunRecoveryAdmin(admin.ModelAdmin):
    list_display = ("taskflow_run_id", "run_start_time", "completion_time", "original_status", 
                    "final_status", "recovered_by", "recovered_at", "is_active")
    list_filter = ("original_status", "final_status", "is_active", "recovered_at")
    search_fields = ("taskflow_run_id", "recovered_by", "recovery_notes")
    list_editable = ("is_active",)
    readonly_fields = ("recovered_at",)
    date_hierarchy = "recovered_at"
    
    fieldsets = (
        ("Run Information", {
            "fields": ("taskflow_run_id", "run_start_time", "completion_time", "original_status")
        }),
        ("Recovery Details", {
            "fields": ("recovered_by", "recovered_at", "recovery_notes", "final_status")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
    )