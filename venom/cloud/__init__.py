"""
VENOM Multi-Cloud Integration Module
Supports AWS, Azure, and GCP cloud deployments
"""

# Import cloud modules
try:
    from venom.cloud import aws
except ImportError:
    aws = None

try:
    from venom.cloud import azure
except ImportError:
    azure = None

try:
    from venom.cloud import gcp
except ImportError:
    gcp = None

__all__ = ['aws', 'azure', 'gcp']
