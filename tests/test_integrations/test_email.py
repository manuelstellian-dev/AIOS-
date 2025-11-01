"""Tests for Email Integration"""
import pytest
from unittest.mock import Mock, patch, MagicMock

# Import email integration
try:
    from venom.integrations.email import EmailIntegration
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    EmailIntegration = None


@pytest.mark.skipif(not EMAIL_AVAILABLE, reason="Email integration not available")
def test_send_email_plain():
    """Test sending plain text email"""
    with patch('venom.integrations.email.smtplib.SMTP') as mock_smtp:
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email = EmailIntegration(
            smtp_host="smtp.test.com",
            smtp_port=587,
            username="test@example.com",
            password="password"
        )
        
        result = email.send_email(
            to="recipient@example.com",
            subject="Test Subject",
            body="Test body"
        )
        
        assert result is True
        mock_server.sendmail.assert_called_once()
        mock_server.starttls.assert_called_once()


@pytest.mark.skipif(not EMAIL_AVAILABLE, reason="Email integration not available")
def test_send_email_html():
    """Test sending HTML email"""
    with patch('venom.integrations.email.smtplib.SMTP') as mock_smtp:
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email = EmailIntegration(
            smtp_host="smtp.test.com",
            smtp_port=587,
            username="test@example.com",
            password="password"
        )
        
        result = email.send_email(
            to="recipient@example.com",
            subject="Test HTML",
            body="<h1>Test</h1>",
            html=True
        )
        
        assert result is True
        mock_server.sendmail.assert_called_once()


@pytest.mark.skipif(not EMAIL_AVAILABLE, reason="Email integration not available")
def test_send_with_attachments():
    """Test sending email with attachments"""
    with patch('venom.integrations.email.smtplib.SMTP') as mock_smtp:
        with patch('venom.integrations.email.os.path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                # Mock file and SMTP server
                mock_open.return_value.__enter__.return_value.read.return_value = b"file content"
                mock_server = MagicMock()
                mock_smtp.return_value.__enter__.return_value = mock_server
                
                email = EmailIntegration(
                    smtp_host="smtp.test.com",
                    smtp_port=587,
                    username="test@example.com",
                    password="password"
                )
                
                result = email.send_email(
                    to="recipient@example.com",
                    subject="Test with attachment",
                    body="Body",
                    attachments=["/tmp/test.txt"]
                )
                
                assert result is True
                mock_server.sendmail.assert_called_once()


@pytest.mark.skipif(not EMAIL_AVAILABLE, reason="Email integration not available")
def test_send_alert():
    """Test sending alert email"""
    with patch('venom.integrations.email.smtplib.SMTP') as mock_smtp:
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email = EmailIntegration(
            smtp_host="smtp.test.com",
            smtp_port=587,
            username="test@example.com",
            password="password"
        )
        
        result = email.send_alert(
            to="admin@example.com",
            alert_type="error",
            message="Test error",
            details="Additional details"
        )
        
        assert result is True
        mock_server.sendmail.assert_called_once()
        
        # Verify HTML email was sent
        call_args = mock_server.sendmail.call_args[0]
        email_content = call_args[2]
        # Email is base64 encoded in MIME format, so check for MIME parts and html keyword
        assert "text/html" in email_content
        assert "ERROR" in email_content or "error" in email_content.lower()


@pytest.mark.skipif(not EMAIL_AVAILABLE, reason="Email integration not available")
def test_connection():
    """Test SMTP connection testing"""
    with patch('venom.integrations.email.smtplib.SMTP') as mock_smtp:
        # Mock successful connection
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email = EmailIntegration(
            smtp_host="smtp.test.com",
            smtp_port=587,
            username="test@example.com",
            password="password"
        )
        
        result = email.test_connection()
        
        assert result is True
        mock_server.login.assert_called_once()
        mock_server.starttls.assert_called_once()


@pytest.mark.skipif(not EMAIL_AVAILABLE, reason="Email integration not available")
def test_ssl_connection():
    """Test SSL connection (port 465)"""
    with patch('venom.integrations.email.smtplib.SMTP_SSL') as mock_smtp:
        # Mock SSL SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        email = EmailIntegration(
            smtp_host="smtp.test.com",
            smtp_port=465,
            username="test@example.com",
            password="password",
            use_tls=False
        )
        
        result = email.send_email(
            to="recipient@example.com",
            subject="Test SSL",
            body="Test body"
        )
        
        assert result is True
        mock_server.sendmail.assert_called_once()
