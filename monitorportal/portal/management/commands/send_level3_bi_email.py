"""
Management command to send Level3 BI report via email
Usage: python manage.py send_level3_bi_email [--recipients email1,email2] [--screenshot]
"""

from django.core.management.base import BaseCommand
from portal.services.email_service import EmailReportService
import sys


class Command(BaseCommand):
    help = 'Send Level3 BI report via email to configured recipients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipients',
            type=str,
            help='Comma-separated list of email recipients (overrides default)',
        )
        parser.add_argument(
            '--screenshot',
            action='store_true',
            help='Include screenshot attachment if failures detected',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Send test email to verify configuration',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('=' * 70)
        )
        self.stdout.write(
            self.style.HTTP_INFO('Level3 BI Email Report Service')
        )
        self.stdout.write(
            self.style.HTTP_INFO('=' * 70)
        )
        
        # Parse recipients
        recipients = None
        if options.get('recipients'):
            recipients = [email.strip() for email in options['recipients'].split(',')]
            self.stdout.write(f"Recipients: {', '.join(recipients)}")
        else:
            self.stdout.write(f"Using default recipients: {', '.join(EmailReportService.DEFAULT_RECIPIENTS)}")
        
        # Create email service
        email_service = EmailReportService(recipients=recipients)
        
        # Send test email if requested
        if options.get('test'):
            self.stdout.write(self.style.WARNING('\nSending test email...'))
            result = email_service.send_test_email()
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {result["message"]}')
                )
                return
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ {result["message"]}')
                )
                sys.exit(1)
        
        # Send Level3 BI report
        include_screenshot = options.get('screenshot', False)
        
        if include_screenshot:
            self.stdout.write(self.style.WARNING('\nScreenshot feature enabled (requires Selenium)'))
        
        self.stdout.write('\nFetching Level3 BI data...')
        
        try:
            result = email_service.send_level3_bi_report(include_screenshot=include_screenshot)
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✓ {result["message"]}')
                )
                
                if result['has_failures']:
                    self.stdout.write(
                        self.style.ERROR('\n⚠️  FAILURES DETECTED in the report!')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('\n✓ All systems normal - No failures detected')
                    )
                
                self.stdout.write(
                    self.style.HTTP_INFO(f'\nEmails sent: {result["sent_count"]}')
                )
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'\n✗ {result["message"]}')
                )
                sys. exit(1)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n✗ Unexpected error: {str(e)}')
            )
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        self.stdout.write(
            self.style.HTTP_INFO('\n' + '=' * 70)
        )
        self.stdout.write(
            self.style.SUCCESS('Email report completed successfully!')
        )
        self.stdout.write(
            self.style.HTTP_INFO('=' * 70 + '\n')
        )
