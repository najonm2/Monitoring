"""
Django management command to sync Informatica Cloud ERP task status

Usage:
    python manage.py sync_informatica_erp_tasks [--cleanup-only]

Run this periodically (e.g., every 6 hours) via:
    - Celery beat task
    - Cron job
    - Django APScheduler
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from portal.services.informatica_cloud_service import (
    InformaticaCloudAPI,
    get_informatica_task_status,
)
from portal.models import InformaticaTaskStatus


class Command(BaseCommand):
    help = 'Sync Informatica Cloud ERP task status (suspended/restarted tasks only)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup-only',
            action='store_true',
            help='Only cleanup expired records, do not fetch from API'
        )
        parser.add_argument(
            '--no-cleanup',
            action='store_true',
            help='Do not cleanup expired records'
        )
        parser.add_argument(
            '--show-summary',
            action='store_true',
            help='Show current summary of stored tasks'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        
        cleanup_only = options.get('cleanup_only', False)
        no_cleanup = options.get('no_cleanup', False)
        show_summary = options.get('show_summary', False)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{'='*70}\n'
                f'Informatica Cloud ERP Task Sync\n'
                f'Started: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'{'='*70}\n'
            )
        )
        
        # Show summary if requested
        if show_summary:
            self.show_summary()
        
        # Cleanup expired records
        if not no_cleanup:
            self.cleanup_expired()
        
        # Fetch from API and sync (unless cleanup-only)
        if not cleanup_only:
            self.sync_from_api()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{'='*70}\n'
                f'Sync completed at {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'{'='*70}\n'
            )
        )
    
    def sync_from_api(self):
        """Fetch from Informatica Cloud API and store ERP tasks"""
        
        self.stdout.write('\n📡 Fetching from Informatica Cloud API...\n')
        
        api = InformaticaCloudAPI()
        
        # Check credentials
        if not api.is_configured():
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Informatica Cloud API credentials not configured\n'
                    '   Set INFORMATICA_CLOUD_USER and INFORMATICA_CLOUD_PASSWORD in settings\n'
                )
            )
            return
        
        result = api.sync_task_status()
        
        if result.get('status') == 'error':
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Error: {result.get('message')}\n"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {result.get('message')}\n"
                    f"   - Total tasks from API: {result.get('tasks_processed')}\n"
                    f"   - ERP tasks stored: {result.get('erp_tasks_stored')}\n"
                    f"   - ERP tasks updated: {result.get('erp_tasks_updated')}\n"
                )
            )
    
    def cleanup_expired(self):
        """Delete records older than 2 days"""
        
        self.stdout.write('\n🗑️  Cleaning up expired records...\n')
        
        expired_count, deleted_info = InformaticaTaskStatus.cleanup_expired()
        
        if expired_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Deleted {expired_count} expired record(s)\n"
                    f"   - Freed disk space and maintained 2-day retention policy\n"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ No expired records found\n"
                )
            )
    
    def show_summary(self):
        """Display summary of stored ERP tasks"""
        
        self.stdout.write('\n📊 Current ERP Task Summary:\n')
        
        summary = InformaticaTaskStatus.get_erp_summary()
        
        self.stdout.write(
            f"   Total stored:        {summary.get('total_stored', 0)}\n"
            f"   Currently suspended: {summary.get('currently_suspended', 0)}\n"
            f"   Total restarted:     {summary.get('total_restarted', 0)}\n"
            f"   Completed (post-restart): {summary.get('completed_after_restart', 0)}\n"
            f"   Failed (post-restart):    {summary.get('failed_after_restart', 0)}\n"
            f"   Updated today:       {summary.get('today_updates', 0)}\n"
        )
        
        # Show recent suspended tasks
        suspended = InformaticaTaskStatus.get_suspended_tasks()[:5]
        if suspended:
            self.stdout.write('\n   Recent suspended tasks:\n')
            for task in suspended:
                self.stdout.write(
                    f"     - {task.task_name} (suspended {task.original_suspend_at})\n"
                )
        
        # Show recent restarts
        restarted = InformaticaTaskStatus.get_restarted_tasks()[:5]
        if restarted:
            self.stdout.write('\n   Recent restarts:\n')
            for task in restarted:
                status = task.restart_completed_status or 'UNKNOWN'
                self.stdout.write(
                    f"     - {task.task_name} restarted at {task.restart_completed_at} (Status: {status})\n"
                )
