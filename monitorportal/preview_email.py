"""
Preview saved emails in your web browser
Opens the latest email as an HTML file
"""

import os
import glob
import webbrowser
import tempfile
from email import message_from_file

def preview_email(email_file_path):
    """Extract HTML from email and open in browser"""
    print(f"Opening: {os.path.basename(email_file_path)}")
    
    try:
        # Read the email file
        with open(email_file_path, 'r', encoding='utf-8') as f:
            msg = message_from_file(f)
        
        # Extract HTML content
        html_content = None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    html_content = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            if msg.get_content_type() == 'text/html':
                html_content = msg.get_payload(decode=True).decode('utf-8')
        
        if not html_content:
            print("No HTML content found in email")
            return False
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
        
        # Open in browser
        print(f"\n✓ Opening email in browser...")
        print(f"  Subject: {msg['Subject']}")
        print(f"  To: {msg['To']}")
        print(f"  From: {msg['From']}")
        
        webbrowser.open('file://' + temp_path)
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Preview saved emails in browser')
    parser.add_argument('--file', help='Preview specific email file')
    parser.add_argument('--dir', default='sent_emails', help='Directory containing email files')
    
    args = parser.parse_args()
    
    sent_emails_dir = args.dir
    
    if not os.path.exists(sent_emails_dir):
        print(f"❌ Directory not found: {sent_emails_dir}")
        return 1
    
    if args.file:
        email_file = args.file
    else:
        # Get latest email
        pattern = os.path.join(sent_emails_dir, '*.log')
        files = glob.glob(pattern)
        
        if not files:
            print("📭 No emails found")
            print("\nGenerate emails with: python manage.py send_level3_bi_email")
            return 0
        
        email_file = max(files, key=os.path.getmtime)
        print(f"📧 Latest email: {os.path.basename(email_file)}\n")
    
    if preview_email(email_file):
        print("\n✅ Email preview opened in browser")
    else:
        print("\n❌ Failed to preview email")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
