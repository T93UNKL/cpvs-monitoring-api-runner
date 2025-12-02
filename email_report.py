#!/usr/bin/env python3
"""
Email Report Sender for CPVS Monitoring

This script sends the monitoring report via email after you manually run the monitoring.
Keeps email sending separate and controlled - you decide when to send.

Usage:
    python email_report.py --report monitoring_report.json --recipients user1@example.com user2@example.com
"""

import json
import argparse
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailReporter:
    """Email reporter for monitoring results"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def load_report(self, report_file: str) -> dict:
        """Load the JSON report"""
        try:
            with open(report_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Report file not found: {report_file}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in report file: {report_file}")
            sys.exit(1)
    
    def format_email_body(self, report: dict) -> str:
        """Format the report as email body"""
        summary = report['summary']
        
        # Determine status emoji
        if summary['failed'] == 0:
            status_emoji = "✅"
            status_text = "ALL SYSTEMS OPERATIONAL"
        else:
            status_emoji = "⚠️"
            status_text = "SOME APIS FAILED"
        
        body = f"""<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: {'#4CAF50' if summary['failed'] == 0 else '#f44336'}; color: white; padding: 20px; text-align: center; }}
        .summary {{ padding: 20px; background-color: #f5f5f5; margin: 20px 0; }}
        .summary-item {{ margin: 10px 0; }}
        .api-item {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .success {{ border-left: 5px solid #4CAF50; }}
        .failed {{ border-left: 5px solid #f44336; }}
        .label {{ font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{status_emoji} CPVS Monitoring Report</h1>
        <h2>{status_text}</h2>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-item"><span class="label">Execution Time:</span> {summary['execution_timestamp']}</div>
        <div class="summary-item"><span class="label">Base URL:</span> {summary['base_url']}</div>
        <div class="summary-item"><span class="label">Total APIs:</span> {summary['total_apis']}</div>
        <div class="summary-item"><span class="label">Successful:</span> <span style="color: #4CAF50;">{summary['successful']}</span></div>
        <div class="summary-item"><span class="label">Failed:</span> <span style="color: #f44336;">{summary['failed']}</span></div>
        <div class="summary-item"><span class="label">Success Rate:</span> {summary['success_rate']}</div>
        <div class="summary-item"><span class="label">Average Response Time:</span> {summary['average_response_time_ms']} ms</div>
    </div>
    
    <h2>Individual API Results</h2>
    <table>
        <tr>
            <th>API Name</th>
            <th>Method</th>
            <th>Status</th>
            <th>Response Time</th>
            <th>HTTP Status</th>
        </tr>
"""
        
        for result in report['detailed_results']:
            status_class = 'success' if result['status'] == 'SUCCESS' else 'failed'
            status_color = '#4CAF50' if result['status'] == 'SUCCESS' else '#f44336'
            response_time = f"{result.get('response_time_ms', 'N/A')} ms" if 'response_time_ms' in result else 'N/A'
            http_status = result.get('status_code', 'N/A')
            
            body += f"""
        <tr class="{status_class}">
            <td>{result['name']}</td>
            <td>{result['method']}</td>
            <td style="color: {status_color}; font-weight: bold;">{result['status']}</td>
            <td>{response_time}</td>
            <td>{http_status}</td>
        </tr>
"""
        
        body += """
    </table>
    
    <div style="margin-top: 30px; padding: 15px; background-color: #e3f2fd; border-radius: 5px;">
        <p><strong>Note:</strong> This is an automated monitoring report. For detailed API responses, please refer to the attached JSON file.</p>
        <p><strong>Report Generated:</strong> {}</p>
    </div>
</body>
</html>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return body
    
    def send_email(self, recipients: list, subject: str, body: str, attachment_path: str = None):
        """Send email with report"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Attach HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Attach JSON file if provided
            if attachment_path:
                try:
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment_path.split("/")[-1]}'
                        )
                        msg.attach(part)
                    logger.info(f"Attached report file: {attachment_path}")
                except Exception as e:
                    logger.warning(f"Could not attach file {attachment_path}: {e}")
            
            # Send email
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            logger.info(f"Sending email to {', '.join(recipients)}")
            server.send_message(msg)
            server.quit()
            
            logger.info("✅ Email sent successfully!")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ SMTP Authentication failed. Check your email and password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Send CPVS monitoring report via email'
    )
    parser.add_argument(
        '--report',
        default='monitoring_report.json',
        help='Path to the monitoring report JSON file (default: monitoring_report.json)'
    )
    parser.add_argument(
        '--recipients',
        nargs='+',
        required=True,
        help='Email recipients (space-separated)'
    )
    parser.add_argument(
        '--smtp-server',
        default='smtp.gmail.com',
        help='SMTP server (default: smtp.gmail.com)'
    )
    parser.add_argument(
        '--smtp-port',
        type=int,
        default=587,
        help='SMTP port (default: 587)'
    )
    parser.add_argument(
        '--sender-email',
        required=True,
        help='Sender email address'
    )
    parser.add_argument(
        '--sender-password',
        required=True,
        help='Sender email password or app password'
    )
    parser.add_argument(
        '--subject',
        default='CPVS Monitoring Report - {date}',
        help='Email subject (default: CPVS Monitoring Report - {date})'
    )
    parser.add_argument(
        '--attach',
        action='store_true',
        help='Attach the JSON report file'
    )
    
    args = parser.parse_args()
    
    # Create email reporter
    reporter = EmailReporter(
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        sender_email=args.sender_email,
        sender_password=args.sender_password
    )
    
    # Load report
    logger.info(f"Loading report from {args.report}")
    report = reporter.load_report(args.report)
    
    # Format email subject
    subject = args.subject.format(date=datetime.now().strftime("%Y-%m-%d %H:%M"))
    if report['summary']['failed'] > 0:
        subject = "⚠️ " + subject + " - FAILURES DETECTED"
    else:
        subject = "✅ " + subject + " - All OK"
    
    # Format email body
    logger.info("Formatting email body")
    body = reporter.format_email_body(report)
    
    # Send email
    attachment = args.report if args.attach else None
    success = reporter.send_email(
        recipients=args.recipients,
        subject=subject,
        body=body,
        attachment_path=attachment
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
