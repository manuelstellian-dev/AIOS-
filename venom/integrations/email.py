"""
VENOM Email Integration
Email integration via SMTP with TLS support
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Union, List, Optional
import time


class EmailIntegration:
    """
    Email integration for sending notifications via SMTP
    
    Features:
    - SMTP with TLS/SSL support
    - Plain text and HTML emails
    - Multiple recipients (to, cc, bcc)
    - Attachment support
    - Email templates for alerts
    - Connection testing
    
    Example:
        email = EmailIntegration(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="bot@example.com",
            password="app_password"
        )
        email.send_email(
            to="admin@example.com",
            subject="Test",
            body="Hello from VENOM!"
        )
    """
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int = 587,
        username: str = None,
        password: str = None,
        use_tls: bool = True,
        from_addr: str = None
    ):
        """
        Initialize email integration
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (default: 587 for TLS)
            username: SMTP username (optional)
            password: SMTP password (optional)
            use_tls: Use TLS encryption (default: True)
            from_addr: From email address (defaults to username)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_addr = from_addr or username or "noreply@venom.ai"
    
    def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        html: bool = False,
        attachments: List[str] = None,
        cc: Union[str, List[str]] = None,
        bcc: Union[str, List[str]] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to: Recipient email(s)
            subject: Email subject
            body: Email body (plain text or HTML)
            html: If True, body is treated as HTML (default: False)
            attachments: List of file paths to attach (optional)
            cc: CC recipient email(s) (optional)
            bcc: BCC recipient email(s) (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # Normalize recipients to lists
        to_list = [to] if isinstance(to, str) else to
        cc_list = [cc] if isinstance(cc, str) and cc else (cc if cc else [])
        bcc_list = [bcc] if isinstance(bcc, str) and bcc else (bcc if bcc else [])
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = ', '.join(to_list)
        if cc_list:
            msg['Cc'] = ', '.join(cc_list)
        msg['Subject'] = subject
        
        # Attach body
        mime_type = 'html' if html else 'plain'
        msg.attach(MIMEText(body, mime_type))
        
        # Attach files
        if attachments:
            for file_path in attachments:
                if not os.path.exists(file_path):
                    continue
                
                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
                except Exception:
                    # Skip attachment on error
                    pass
        
        # Send email
        try:
            # Combine all recipients
            all_recipients = to_list + cc_list + bcc_list
            
            if self.use_tls:
                # TLS connection
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.sendmail(self.from_addr, all_recipients, msg.as_string())
            else:
                # Non-TLS connection (port 25 or SSL port 465)
                if self.smtp_port == 465:
                    # SSL
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL(
                        self.smtp_host, 
                        self.smtp_port, 
                        context=context,
                        timeout=10
                    ) as server:
                        if self.username and self.password:
                            server.login(self.username, self.password)
                        server.sendmail(self.from_addr, all_recipients, msg.as_string())
                else:
                    # Plain SMTP
                    with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                        if self.username and self.password:
                            server.login(self.username, self.password)
                        server.sendmail(self.from_addr, all_recipients, msg.as_string())
            
            return True
        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"Email send error: {e}")
            return False
    
    def send_alert(
        self,
        to: Union[str, List[str]],
        alert_type: str,
        message: str,
        details: str = None
    ) -> bool:
        """
        Send a formatted alert email
        
        Args:
            to: Recipient email(s)
            alert_type: Type of alert (info, warning, error, success)
            message: Alert message
            details: Optional additional details
            
        Returns:
            True if email sent successfully
        """
        # Alert templates
        alert_config = {
            "info": {"emoji": "ℹ️", "color": "#2196F3"},
            "warning": {"emoji": "⚠️", "color": "#FF9800"},
            "error": {"emoji": "❌", "color": "#F44336"},
            "success": {"emoji": "✅", "color": "#4CAF50"}
        }
        
        config = alert_config.get(alert_type, alert_config["info"])
        
        subject = f"{config['emoji']} VENOM Alert: {alert_type.upper()}"
        
        # HTML body with styling
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-box {{
                    border-left: 4px solid {config['color']};
                    padding: 15px;
                    margin: 20px 0;
                    background-color: #f5f5f5;
                }}
                .alert-header {{
                    font-size: 18px;
                    font-weight: bold;
                    color: {config['color']};
                    margin-bottom: 10px;
                }}
                .alert-message {{
                    font-size: 14px;
                    margin-bottom: 10px;
                }}
                .alert-details {{
                    font-size: 12px;
                    color: #666;
                    padding: 10px;
                    background-color: #fff;
                    border-radius: 4px;
                }}
                .footer {{
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <div class="alert-header">
                    {config['emoji']} {alert_type.upper()} ALERT
                </div>
                <div class="alert-message">
                    {message}
                </div>
                {f'<div class="alert-details">{details}</div>' if details else ''}
            </div>
            <div class="footer">
                Sent from VENOM at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to, subject, html_body, html=True)
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection without sending email
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.use_tls:
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    if self.username and self.password:
                        server.login(self.username, self.password)
            else:
                if self.smtp_port == 465:
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL(
                        self.smtp_host,
                        self.smtp_port,
                        context=context,
                        timeout=10
                    ) as server:
                        if self.username and self.password:
                            server.login(self.username, self.password)
                else:
                    with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                        if self.username and self.password:
                            server.login(self.username, self.password)
            return True
        except Exception as e:
            print(f"Connection test error: {e}")
            return False
