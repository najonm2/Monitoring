"""
Helper script to send saved email files via SMTP
This can be run by someone with network access to mailrelay.corp.intranet
or copied to a server with SMTP access.

Usage:
    python send_saved_emails.py                    # Send all unsent emails
    python send_saved_emails.py --file <filename>  # Send specific email file
    python send_saved_emails.py --latest           # Send only the latest email
"""

import smtplib
import os
import sys
import glob
from email import message_from_file

# SMTP Configuration (same as in your working example)
SMTP_HOST = "mailrelay.corp.intranet"
SMTP_PORT = 25
FROM_EMAIL = "naresh.m@lumen.com"

def send_email_file(email_file_path):
    """Send an email from a saved .eml or .log file"""
    print(f"\n{'='*70}")
    print(f"Processing: {os.path.basename(email_file_path)}")
    print(f"{'='*70}")
    
    try:
        # Read the email file
        with open(email_file_path, 'r', encoding='utf-8') as f:
            msg = message_from_file(f)
        
        # Extract recipients
        to_emails = msg['To'].split(', ') if msg['To'] else []
        
        if not to_emails:
            print("❌ No recipients found in email")
            return False
        
        print(f"From: {msg['From']}")
        print(f"To: {', '.join(to_emails)}")
        print(f"Subject: {msg['Subject']}")
        
        # Connect and send
        print(f"\nConnecting to SMTP server at {SMTP_HOST}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        
        print("Sending email...")
        server.sendmail(FROM_EMAIL, to_emails, msg.as_string())
        server.quit()
        
        print(f"✅ Email sent successfully to {len(to_emails)} recipient(s)")
        
        # Mark as sent by renaming file
        sent_path = email_file_path + '.sent'
        os.rename(email_file_path, sent_path)
        print(f"✓ Marked as sent: {os.path.basename(sent_path)}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {email_file_path}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_email_files(sent_emails_dir, include_sent=False):
    """Get list of email files to send"""
    pattern = os.path.join(sent_emails_dir, '*.log')
    files = glob.glob(pattern)
    
    if not include_sent:
        # Exclude already sent files
        files = [f for f in files if not os.path.exists(f + '.sent')]
    
    return sorted(files, key=os.path.getmtime)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Send saved email files via SMTP')
    parser.add_argument('--file', help='Send specific email file')
    parser.add_argument('--latest', action='store_true', help='Send only the latest email')
    parser.add_argument('--all', action='store_true', help='Include already sent emails')
    parser.add_argument('--dir', default='sent_emails', help='Directory containing email files')
    
    args = parser.parse_args()
    
    sent_emails_dir = args.dir
    
    if not os.path.exists(sent_emails_dir):
        print(f"❌ Directory not found: {sent_emails_dir}")
        print(f"   Make sure you're in the monitorportal directory")
        sys.exit(1)
    
    print("="*70)
    print("      Level3 BI Email Sender (SMTP)")
    print("="*70)
    print(f"SMTP Server: {SMTP_HOST}:{SMTP_PORT}")
    print(f"From: {FROM_EMAIL}")
    print("="*70)
    
    # Determine which files to send
    if args.file:
        # Send specific file
        email_files = [args.file] if os.path.exists(args.file) else []
    elif args.latest:
        # Send only the latest
        all_files = get_email_files(sent_emails_dir, args.all)
        email_files = [all_files[-1]] if all_files else []
    else:
        # Send all unsent
        email_files = get_email_files(sent_emails_dir, args.all)
    
    if not email_files:
        print("\n📭 No emails to send")
        print("\nTip: Generate emails first with:")
        print("     python manage.py send_level3_bi_email")
        sys.exit(0)
    
    print(f"\n📧 Found {len(email_files)} email(s) to send")
    
    # Send each email
    success_count = 0
    fail_count = 0
    
    for email_file in email_files:
        if send_email_file(email_file):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Sent successfully: {success_count}")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count}")
    print("="*70)
    
    return 0 if fail_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
