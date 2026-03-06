"""
Management command for training AI models.

Usage:
    python manage.py train_ai_models
    python manage.py train_ai_models --lookback-days 180
"""

from django.core.management.base import BaseCommand
import logging

from portal.ai.training import train_all_models, fetch_training_data

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Train all AI models on historical data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lookback-days',
            type=int,
            default=90,
            help='Number of days of historical data to use for training'
        )

    def handle(self, *args, **options):
        lookback_days = options['lookback_days']

        self.stdout.write(self.style.SUCCESS(
            f'🎓 Training AI Models with {lookback_days} days of data'
        ))

        try:
            # Fetch training data
            self.stdout.write('Fetching training data...')
            training_data = fetch_training_data(lookback_days=lookback_days)
            self.stdout.write(self.style.SUCCESS(
                f'✓ Fetched {len(training_data)} records'
            ))

            # Train models
            self.stdout.write('\nTraining models (this may take several minutes)...')
            results = train_all_models(training_data=training_data)

            # Display results
            self.stdout.write('\n' + '='*50)
            self.stdout.write('Training Results:')
            self.stdout.write('='*50)
            
            for agent_name, success in results.items():
                if success:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ {agent_name}: SUCCESS'
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f'  ✗ {agent_name}: FAILED'
                    ))

            success_count = sum(1 for v in results.values() if v)
            total_count = len(results)

            self.stdout.write('\n' + '='*50)
            if success_count == total_count:
                self.stdout.write(self.style.SUCCESS(
                    f'🎉 All {total_count} models trained successfully!'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'⚠ {success_count}/{total_count} models trained successfully'
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'\n✗ Training failed: {str(e)}'
            ))
            logger.error(f"Model training failed: {str(e)}", exc_info=True)
            raise
