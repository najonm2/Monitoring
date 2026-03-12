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


class ERPRunRecovery(models.Model):
    """
    Track manual recovery actions for ERP runs that were suspended/failed
    but later completed successfully through manual intervention.
    """
    taskflow_run_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="IICS TASKFLOW_RUN_ID that was recovered"
    )
    run_start_time = models.DateTimeField(
        help_text="Original run start time (MST)"
    )
    completion_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the run actually completed (after manual recovery)"
    )
    original_status = models.CharField(
        max_length=50,
        default="SUSPENDED",
        help_text="Status before recovery (SUSPENDED, FAILED, etc.)"
    )
    recovered_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this recovery was marked in the system"
    )
    recovered_by = models.CharField(
        max_length=200,
        help_text="Person who recovered the run (email or name)"
    )
    recovery_notes = models.TextField(
        blank=True,
        help_text="Notes about what was done to recover the run"
    )
    final_status = models.CharField(
        max_length=50,
        default="SUCCESS",
        help_text="Status after recovery (SUCCESS, PARTIAL, etc.)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Set to False if recovery entry should be hidden"
    )

    class Meta:
        ordering = ["-recovered_at"]
        verbose_name = "ERP Run Recovery"
        verbose_name_plural = "ERP Run Recoveries"

    def __str__(self):
        return f"Recovery: {self.taskflow_run_id} ({self.original_status} → {self.final_status})"


class InformaticaTaskStatus(models.Model):
    """
    Store Informatica Cloud API task status (ERP-related only)
    
    Purpose:
    - Capture suspended and restart data from Informatica Cloud API
    - Store only ERP-related workflows and tasks
    - Auto-cleanup after 2 days (512MB max growth)
    
    Fields captured from API:
    - Task ID (unique identifier)
    - Task name & workflow info
    - Status (SUSPENDED, COMPLETED, RUNNING, FAILED, etc.)
    - Restart count and timestamps
    - Restart completion status
    
    Storage:
    - Max ~500 rows per day for ERP (estimated 50KB per day)
    - 2-day retention = ~100KB before cleanup
    - Auto-deletes expired records daily
    """
    
    # Task identifiers from Informatica API
    task_id = models.CharField(
        max_length=200, 
        unique=True,
        db_index=True,
        help_text="Task ID from Informatica Cloud API /tf/status/"
    )
    task_name = models.CharField(
        max_length=500,
        help_text="Workflow or task name"
    )
    
    # Status from API
    status = models.CharField(
        max_length=50,
        choices=[
            ('SUSPENDED', 'Suspended'),
            ('COMPLETED', 'Completed'),
            ('RUNNING', 'Running'),
            ('FAILED', 'Failed'),
            ('RESTARTED', 'Restarted'),
            ('UNKNOWN', 'Unknown'),
        ],
        default='SUSPENDED',
        db_index=True,
        help_text="Current status from Informatica Cloud API"
    )
    
    # ERP-specific filtering
    is_erp_related = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Only ERP-related tasks stored (not all workloads)"
    )
    erp_location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="ERP location: CDW_DSL_ERP, CDW_ASL_SAPS4, ASL_ERP_DATAHUB, etc."
    )
    workflow_name = models.CharField(
        max_length=500,
        db_index=True,
        blank=True,
        null=True,
        help_text="ERP workflow name containing 'ERP', 'SAPS4', 'DATAHUB'"
    )
    
    # Restart tracking (primary use case)
    restart_count = models.IntegerField(
        default=0,
        help_text="Number of times this task was restarted"
    )
    original_suspend_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When task was originally suspended"
    )
    last_restart_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text="Timestamp of last restart attempt"
    )
    restart_completed_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text="When restart was completed"
    )
    restart_completed_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Status after restart: SUCCESS, FAILED, PARTIAL, etc."
    )
    
    # Notes
    restart_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about restart reason or details from API"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When record was first captured"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time from API"
    )
    expires_at = models.DateTimeField(
        db_index=True,
        help_text="Auto-delete record after this date (2 days from creation)"
    )
    
    class Meta:
        db_table = 'informatica_task_status'
        verbose_name = 'Informatica Task Status'
        verbose_name_plural = 'Informatica Task Statuses'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['is_erp_related', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['task_id']),
            models.Index(fields=['workflow_name']),
            models.Index(fields=['restart_completed_at']),
        ]
    
    def __str__(self):
        restart_info = f" (Restart #{self.restart_count})" if self.restart_count > 0 else ""
        return f"{self.task_name} - {self.status}{restart_info}"
    
    def save(self, *args, **kwargs):
        """Auto-set expiration to 2 days if not already set"""
        from datetime import timedelta
        from django.utils import timezone
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=2)
        super().save(*args, **kwargs)
    
    @classmethod
    def cleanup_expired(cls):
        """
        Delete records older than 2 days (retention policy).
        Should be called by periodic task.
        
        Returns:
            tuple: (count, details) of deleted records
        """
        from django.utils import timezone
        
        expired = cls.objects.filter(expires_at__lte=timezone.now())
        count = expired.count()
        deleted = expired.delete()
        return count, deleted
    
    @classmethod
    def get_suspended_tasks(cls):
        """Get all currently suspended ERP tasks"""
        return cls.objects.filter(
            status='SUSPENDED',
            is_erp_related=True
        ).order_by('-updated_at')
    
    @classmethod
    def get_restarted_tasks(cls):
        """Get all restarted ERP tasks with completion data"""
        return cls.objects.filter(
            restart_completed_at__isnull=False,
            is_erp_related=True
        ).order_by('-restart_completed_at')
    
    @classmethod
    def get_erp_summary(cls):
        """Get summary statistics for ERP task tracking"""
        from django.utils import timezone
        from datetime import timedelta
        
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        return {
            'total_stored': cls.objects.filter(is_erp_related=True).count(),
            'currently_suspended': cls.objects.filter(
                status='SUSPENDED',
                is_erp_related=True
            ).count(),
            'total_restarted': cls.objects.filter(
                restart_completed_at__isnull=False,
                is_erp_related=True
            ).count(),
            'completed_after_restart': cls.objects.filter(
                restart_completed_status='SUCCESS',
                is_erp_related=True
            ).count(),
            'failed_after_restart': cls.objects.filter(
                restart_completed_status='FAILED',
                is_erp_related=True
            ).count(),
            'today_updates': cls.objects.filter(
                updated_at__gte=today_start,
                is_erp_related=True
            ).count(),
        }