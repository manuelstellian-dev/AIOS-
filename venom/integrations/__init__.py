"""VENOM Integrations Module - External API integrations"""
from venom.integrations.slack import SlackIntegration
from venom.integrations.email import EmailIntegration
from venom.integrations.webhook import WebhookIntegration
from venom.integrations.database import DatabaseIntegration

__all__ = [
    'SlackIntegration',
    'EmailIntegration',
    'WebhookIntegration',
    'DatabaseIntegration'
]
