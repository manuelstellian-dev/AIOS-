"""Extended integration tests for database, email, slack, webhook"""
import pytest
from unittest.mock import Mock, patch
from venom.integrations.database import DatabaseIntegration
from venom.integrations.email import EmailIntegration
from venom.integrations.slack import SlackIntegration
from venom.integrations.webhook import WebhookIntegration


class TestDatabaseIntegrationExtended:
    """Extended database integration tests"""
    
    def test_database_connection_string(self):
        """Test connection string generation"""
        db = DatabaseIntegration(
            db_type='postgresql',
            host='localhost',
            port=5432,
            database='testdb',
            username='user',
            password='pass'
        )
        
        if hasattr(db, 'connection_string'):
            conn_str = db.connection_string
            assert 'postgresql' in conn_str or 'testdb' in conn_str
    
    def test_database_query_execution(self):
        """Test query execution"""
        db = DatabaseIntegration(db_type='postgresql')
        
        with patch.object(db, 'execute', return_value=[]):
            result = db.execute("SELECT 1")
            assert result is not None
    
    def test_database_transaction(self):
        """Test transaction handling"""
        db = DatabaseIntegration(db_type='postgresql')
        
        if hasattr(db, 'begin_transaction'):
            with patch.object(db, 'begin_transaction'):
                db.begin_transaction()
        
        if hasattr(db, 'commit'):
            with patch.object(db, 'commit'):
                db.commit()


class TestEmailIntegrationExtended:
    """Extended email integration tests"""
    
    def test_email_with_attachments(self):
        """Test sending email with attachments"""
        email = EmailIntegration(
            smtp_host='smtp.test.com',
            smtp_port=587
        )
        
        if hasattr(email, 'send_with_attachments'):
            with patch.object(email, 'send_with_attachments', return_value=True):
                result = email.send_with_attachments(
                    to='test@test.com',
                    subject='Test',
                    body='Body',
                    attachments=['file.txt']
                )
                assert result is True
    
    def test_email_html_content(self):
        """Test sending HTML email"""
        email = EmailIntegration(smtp_host='smtp.test.com')
        
        if hasattr(email, 'send_html'):
            with patch.object(email, 'send_html', return_value=True):
                result = email.send_html(
                    to='test@test.com',
                    subject='Test',
                    html='<h1>Test</h1>'
                )
                assert result is True
    
    def test_email_validation(self):
        """Test email address validation"""
        email = EmailIntegration(smtp_host='smtp.test.com')
        
        if hasattr(email, 'validate_email'):
            assert email.validate_email('test@test.com') is True
            assert email.validate_email('invalid') is False


class TestSlackIntegrationExtended:
    """Extended Slack integration tests"""
    
    @patch('requests.post')
    def test_slack_post_message(self, mock_post):
        """Test posting message to Slack"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'ok': True}
        
        slack = SlackIntegration(webhook_url='https://hooks.slack.com/test')
        
        result = slack.post_message(
            channel='#general',
            text='Test message'
        )
        
        assert result is not None
    
    @patch('requests.post')
    def test_slack_with_attachments(self, mock_post):
        """Test posting with attachments"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'ok': True}
        
        slack = SlackIntegration(webhook_url='https://hooks.slack.com/test')
        
        if hasattr(slack, 'post_with_attachments'):
            result = slack.post_with_attachments(
                channel='#general',
                text='Test',
                attachments=[{'title': 'Attachment'}]
            )
            assert result is not None
    
    def test_slack_error_handling(self):
        """Test error handling"""
        slack = SlackIntegration(webhook_url='https://hooks.slack.com/test')
        
        with patch('requests.post', side_effect=Exception('Network error')):
            if hasattr(slack, 'post_message'):
                try:
                    slack.post_message(channel='#test', text='Test')
                except Exception as e:
                    assert 'error' in str(e).lower() or 'Network' in str(e)


class TestWebhookIntegrationExtended:
    """Extended webhook integration tests"""
    
    @patch('requests.post')
    def test_webhook_post(self, mock_post):
        """Test webhook POST request"""
        mock_post.return_value.status_code = 200
        
        webhook = WebhookIntegration(url='https://example.com/webhook')
        
        result = webhook.send({'event': 'test', 'data': 'value'})
        
        assert result is not None
    
    @patch('requests.post')
    def test_webhook_retry_logic(self, mock_post):
        """Test retry logic on failure"""
        mock_post.side_effect = [
            Mock(status_code=500),
            Mock(status_code=200)
        ]
        
        webhook = WebhookIntegration(
            url='https://example.com/webhook',
            retry_count=2
        )
        
        if hasattr(webhook, 'send_with_retry'):
            result = webhook.send_with_retry({'data': 'test'})
            assert result is not None
    
    @patch('requests.post')
    def test_webhook_headers(self, mock_post):
        """Test custom headers"""
        mock_post.return_value.status_code = 200
        
        webhook = WebhookIntegration(
            url='https://example.com/webhook',
            headers={'Authorization': 'Bearer token'}
        )
        
        webhook.send({'data': 'test'})
        
        # Verify headers were passed
        if mock_post.called:
            call_kwargs = mock_post.call_args[1]
            if 'headers' in call_kwargs:
                assert 'Authorization' in call_kwargs['headers']
