"""
Email Service for Monitor Portal
Sends automated email reports with failure alerts and screenshots
"""

import os
import logging
from datetime import datetime
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from io import BytesIO

logger = logging.getLogger(__name__)


class EmailReportService:
    """
    Service to send email reports for monitoring data
    """
    
    DEFAULT_RECIPIENTS = [
        'Naresh.m@lumen.com',
        'Prithviraj.Nayak@lumen.com'
    ]
    
    def __init__(self, recipients=None):
        """
        Initialize email service
        
        Args:
            recipients (list): List of email addresses. If None, uses DEFAULT_RECIPIENTS
        """
        self.recipients = recipients or self.DEFAULT_RECIPIENTS
        
    def send_level3_bi_report(self, include_screenshot=False):
        """
        Send Level3 BI report via email
        
        Args:
            include_screenshot (bool): Whether to include screenshot attachment
            
        Returns:
            dict: {'success': bool, 'message': str, 'sent_count': int}
        """
        try:
            from portal.services.bi_service import (
                get_level3_bi_feed,
                get_capex_details,
                get_bi_status_query
            )
            from portal.erp_mdm_insights import get_erp_run_history
            
            # Fetch data
            logger.info("Fetching Level3 BI report data...")
            bi_feed_data = get_level3_bi_feed()
            capex_data = get_capex_details()
            bi_status_data = get_bi_status_query()
            erp_data = get_erp_run_history()
            
            # Check if there are any failures
            has_failures = self._check_for_failures(bi_feed_data, capex_data, bi_status_data, erp_data)
            
            # Prepare context for email template
            context = {
                'bi_feed_data': bi_feed_data,
                'capex_data': capex_data,
                'bi_status_data': bi_status_data,
                'erp_data': erp_data,
                'has_failures': has_failures,
                'report_time': datetime.now(),
                'failure_count': self._count_failures(bi_feed_data, capex_data, bi_status_data, erp_data)
            }
            
            # Render email
            html_content = render_to_string('portal/emails/level3_bi_report.html', context)
            text_content = strip_tags(html_content)
            
            # Create subject
            subject = self._create_subject(has_failures, context['failure_count'])
            
            # Create email
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=self.recipients,
            )
            email.content_subtype = 'html'  # Send as HTML
            
            # Add screenshot if requested and failures detected
            if include_screenshot and has_failures:
                screenshot_data = self._capture_screenshot()
                if screenshot_data:
                    email.attach('level3_bi_report.png', screenshot_data, 'image/png')
                    logger.info("Screenshot attached to email")
            
            # Send email
            sent_count = email.send(fail_silently=False)
            
            logger.info(f"Level3 BI report email sent to {len(self.recipients)} recipients")
            
            return {
                'success': True,
                'message': f'Email sent successfully to {len(self.recipients)} recipients',
                'sent_count': sent_count,
                'has_failures': has_failures
            }
            
        except Exception as e:
            logger.error(f"Failed to send Level3 BI report email: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'Failed to send email: {str(e)}',
                'sent_count': 0
            }
    
    def _check_for_failures(self, bi_feed_data, capex_data, bi_status_data, erp_data):
        """
        Check if there are any failures in the data
        
        Returns:
            bool: True if failures detected
        """
        # Check BI Feed for failures
        if bi_feed_data:
            for item in bi_feed_data:
                if item.get('status') in ['Failed', 'No Run', 'ERROR']:
                    return True
                if item.get('met_or_miss') == 'Miss':
                    return True
        
        # Check CAPEX for failures
        if capex_data:
            for item in capex_data:
                if item.get('status') in ['FAILED', 'ERROR']:
                    return True
        
        # Check BI Status for failures
        if bi_status_data:
            for item in bi_status_data:
                if item.get('status') in ['Failed', 'No Run', 'ERROR']:
                    return True
                if item.get('met_or_miss') == 'Miss':
                    return True
        
        # Check ERP for failures
        if erp_data and erp_data.get('success'):
            current_run = erp_data.get('current_run', {})
            if current_run.get('failed', 0) > 0:
                return True
        
        return False
    
    def _count_failures(self, bi_feed_data, capex_data, bi_status_data, erp_data):
        """
        Count total number of failures
        
        Returns:
            int: Total failure count
        """
        count = 0
        
        # Count BI Feed failures
        if bi_feed_data:
            count += sum(1 for item in bi_feed_data 
                        if item.get('status') in ['Failed', 'No Run', 'ERROR'])
            count += sum(1 for item in bi_feed_data 
                        if item.get('met_or_miss') == 'Miss')
        
        # Count CAPEX failures
        if capex_data:
            count += sum(1 for item in capex_data 
                        if item.get('status') in ['FAILED', 'ERROR'])
        
        # Count BI Status failures
        if bi_status_data:
            count += sum(1 for item in bi_status_data 
                        if item.get('status') in ['Failed', 'No Run', 'ERROR'])
            count += sum(1 for item in bi_status_data 
                        if item.get('met_or_miss') == 'Miss')
        
        # Count ERP failures
        if erp_data and erp_data.get('success'):
            current_run = erp_data.get('current_run', {})
            count += current_run.get('failed', 0)
        
        return count
    
    def _create_subject(self, has_failures, failure_count):
        """
        Create email subject based on status
        
        Args:
            has_failures (bool): Whether failures are detected
            failure_count (int): Number of failures
            
        Returns:
            str: Email subject
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        if has_failures:
            return f'🚨 ALERT: Level3 BI Report - {failure_count} Failures Detected ({timestamp})'
        else:
            return f'✅ Level3 BI Report - All Systems Normal ({timestamp})'
    
    def _capture_screenshot(self):
        """
        Capture screenshot of Level3 BI page (requires selenium/playwright)
        
        Returns:
            bytes: Screenshot PNG data or None
        """
        try:
            # Option 1: Using Selenium (requires installation)
            # This is a placeholder - you'll need to install selenium and chromedriver
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Get server URL from settings or use default
            server_url = getattr(settings, 'SERVER_URL', 'http://127.0.0.1:8000')
            page_url = f"{server_url}/level3-bi/"
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(page_url)
            
            # Wait for page to load
            import time
            time.sleep(5)
            
            # Capture screenshot
            screenshot = driver.get_screenshot_as_png()
            driver.quit()
            
            return screenshot
            
        except ImportError:
            logger.warning("Selenium not installed. Screenshot feature disabled. Install with: pip install selenium")
            return None
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {str(e)}")
            return None
    
    def send_test_email(self):
        """
        Send a test email to verify configuration
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            subject = 'Test Email - Monitor Portal Email Service'
            message = f'''
            This is a test email from the Monitor Portal Email Service.
            
            Configuration:
            - From: {settings.DEFAULT_FROM_EMAIL}
            - To: {', '.join(self.recipients)}
            - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            If you received this email, the email service is configured correctly.
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                self.recipients,
                fail_silently=False,
            )
            
            return {
                'success': True,
                'message': f'Test email sent successfully to {len(self.recipients)} recipients'
            }
            
        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send test email: {str(e)}'
            }


def send_scheduled_level3_bi_report():
    """
    Convenience function for scheduled tasks
    Sends Level3 BI report with screenshot if failures detected
    
    Returns:
        bool: True if sent successfully
    """
    email_service = EmailReportService()
    result = email_service.send_level3_bi_report(include_screenshot=True)
    
    if result['success']:
        logger.info(f"Scheduled Level3 BI report sent: {result['message']}")
        if result['has_failures']:
            logger.warning(f"FAILURES DETECTED in Level3 BI report!")
    else:
        logger.error(f"Failed to send scheduled Level3 BI report: {result['message']}")
    
    return result['success']
