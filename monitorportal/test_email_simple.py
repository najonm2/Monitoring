import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    from_email = "naresh.m@lumen.com"
    smtp_host = "mailrelay.corp.intranet"
    smtp_port = 25
    to_emails = ["naresh.m@lumen.com", "Prithviraj.Nayak@lumen.com"]
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test Email - Level3 BI Report System"
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)
    
    body_html = """
    <h3>Test Email</h3>
    <p>This is a test email from the Level3 BI monitoring system.</p>
    <p>If you received this, email is working correctly!</p>
    """
    
    msg.attach(MIMEText(body_html, "html"))
    
    try:
        print("Connecting to SMTP server at {}:{}...".format(smtp_host, smtp_port))
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.sendmail(from_email, to_emails, msg.as_string())
        server.quit()
        print("✓ Email sent successfully to {}".format(", ".join(to_emails)))
    except Exception as e:
        print("✗ Failed to send email: {}".format(str(e)))
        raise

if __name__ == "__main__":
    send_test_email()
