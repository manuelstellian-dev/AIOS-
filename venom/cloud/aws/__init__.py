"""VENOM AWS Cloud Integration"""
from venom.cloud.aws.eks_deployer import EKSDeployer
from venom.cloud.aws.lambda_handler import LambdaDeployer, lambda_handler
from venom.cloud.aws.s3_backup import S3BackupManager

# Backward compatibility alias (LambdaHandler never existed as a class)
LambdaHandler = LambdaDeployer

__all__ = ['EKSDeployer', 'LambdaHandler', 'LambdaDeployer', 'lambda_handler', 'S3BackupManager']
