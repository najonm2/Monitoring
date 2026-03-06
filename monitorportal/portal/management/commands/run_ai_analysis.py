"""
Management command to run AI analysis in background.

Usage:
    python manage.py run_ai_analysis
    python manage.py run_ai_analysis --application level3
    python manage.py run_ai_analysis --continuous
"""

from django.core.management.base import BaseCommand
import time
import logging

from portal.ai.orchestrator import get_orchestrator
from portal.ai.training import load_all_models, check_model_health

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run AI analysis on job data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--application',
            type=str,
            default='all',
            help='Application to analyze (level3, mdm, erp, or all)'
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously with interval'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=15,
            help='Interval in minutes for continuous mode'
        )

    def handle(self, *args, **options):
        application = options['application']
        continuous = options['continuous']
        interval = options['interval']

        self.stdout.write(self.style.SUCCESS(
            '🤖 Starting AI Analysis System'
        ))

        # Load models
        self.stdout.write('Loading AI models...')
        load_results = load_all_models()
        
        loaded_count = sum(1 for v in load_results.values() if v)
        self.stdout.write(self.style.SUCCESS(
            f'✓ Loaded {loaded_count}/{len(load_results)} models'
        ))

        # Check health
        health = check_model_health()
        if health['overall_status'] != 'healthy':
            self.stdout.write(self.style.WARNING(
                f"⚠ System health: {health['overall_status']}"
            ))
            for warning in health.get('warnings', []):
                self.stdout.write(self.style.WARNING(f"  - {warning}"))

        # Run analysis
        if continuous:
            self.stdout.write(self.style.SUCCESS(
                f'Running continuously every {interval} minutes...'
            ))
            self.run_continuous(application, interval)
        else:
            self.run_once(application)

    def run_once(self, application):
        """Run analysis once."""
        try:
            self.stdout.write(f'Analyzing {application} jobs...')
            
            orchestrator = get_orchestrator()
            results = orchestrator.fetch_and_analyze(application)
            
            # Display summary
            summary = results.get('summary', {})
            self.stdout.write(self.style.SUCCESS(
                f"\n✓ Analysis Complete: {summary.get('executive_summary', '')}"
            ))
            
            self.stdout.write(f"\nKey Metrics:")
            metrics = summary.get('key_metrics', {})
            self.stdout.write(f"  - Anomalies: {metrics.get('anomalies_detected', 0)}")
            self.stdout.write(f"  - Predicted Failures: {metrics.get('predicted_failures', 0)}")
            self.stdout.write(f"  - Critical Alerts: {metrics.get('critical_alerts', 0)}")
            self.stdout.write(f"  - High Alerts: {metrics.get('high_alerts', 0)}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)

    def run_continuous(self, application, interval_minutes):
        """Run analysis continuously."""
        interval_seconds = interval_minutes * 60
        
        while True:
            try:
                self.run_once(application)
                
                self.stdout.write(self.style.SUCCESS(
                    f'\nWaiting {interval_minutes} minutes until next run...\n'
                ))
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING(
                    '\n\nStopping AI analysis system...'
                ))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'✗ Error in continuous mode: {str(e)}'
                ))
                logger.error(f"Continuous analysis error: {str(e)}", exc_info=True)
                time.sleep(interval_seconds)
