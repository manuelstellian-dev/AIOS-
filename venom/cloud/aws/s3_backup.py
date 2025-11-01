"""
AWS S3 Backup Manager for VENOM Ω-AIOS
Backup and restore VENOM ledger/state to Amazon S3
"""
import json
import pickle
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Graceful imports
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    ClientError = Exception


class S3BackupManager:
    """
    Backup VENOM ledger and state to Amazon S3
    
    Features:
    - Ledger backup/restore
    - Version management
    - Metadata tracking
    - Encryption support
    """
    
    def __init__(
        self, 
        bucket_name: str, 
        region: str = 'us-east-1',
        prefix: str = 'venom-backups/'
    ):
        """
        Initialize S3 backup manager
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region (default: us-east-1)
            prefix: S3 key prefix (default: venom-backups/)
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for AWS S3 backup. "
                "Install with: pip install boto3"
            )
        
        self.bucket_name = bucket_name
        self.region = region
        self.prefix = prefix.rstrip('/') + '/'
        self.s3_client = boto3.client('s3', region_name=region)
    
    def create_bucket(self) -> bool:
        """
        Create S3 bucket if it doesn't exist
        
        Returns:
            True if successful or already exists, False otherwise
        """
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} already exists")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': self.region
                            }
                        )
                    
                    # Enable versioning
                    self.s3_client.put_bucket_versioning(
                        Bucket=self.bucket_name,
                        VersioningConfiguration={'Status': 'Enabled'}
                    )
                    
                    print(f"Created bucket: {self.bucket_name}")
                    return True
                    
                except ClientError as create_error:
                    print(f"Error creating bucket: {create_error}")
                    return False
            else:
                print(f"Error checking bucket: {e}")
                return False
    
    def backup_ledger(
        self, 
        ledger: 'ImmutableLedger', 
        backup_name: Optional[str] = None
    ) -> str:
        """
        Backup VENOM ledger to S3
        
        Args:
            ledger: ImmutableLedger instance to backup
            backup_name: Optional custom backup name (default: timestamp-based)
            
        Returns:
            S3 key of the backup
        """
        # Generate backup name if not provided
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_name = f"ledger-{timestamp}"
        
        # Add .pkl extension if not present
        if not backup_name.endswith('.pkl'):
            backup_name += '.pkl'
        
        s3_key = self.prefix + backup_name
        
        try:
            # Serialize ledger
            ledger_data = {
                'chain': [entry.to_dict() for entry in ledger.chain],
                'version': '0.2.0',
                'backup_timestamp': time.time(),
                'chain_length': len(ledger.chain)
            }
            
            # Convert to bytes
            serialized_data = pickle.dumps(ledger_data)
            
            # Create metadata
            metadata = {
                'venom-version': '0.2.0',
                'chain-length': str(len(ledger.chain)),
                'backup-timestamp': str(time.time())
            }
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=serialized_data,
                Metadata=metadata,
                ContentType='application/octet-stream'
            )
            
            print(f"Backed up ledger to s3://{self.bucket_name}/{s3_key}")
            return s3_key
            
        except ClientError as e:
            raise RuntimeError(f"Failed to backup ledger: {e}")
    
    def restore_ledger(self, backup_key: str) -> 'ImmutableLedger':
        """
        Restore VENOM ledger from S3 backup
        
        Args:
            backup_key: S3 key of the backup
            
        Returns:
            Restored ImmutableLedger instance
        """
        try:
            # Download from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=backup_key
            )
            
            # Deserialize
            serialized_data = response['Body'].read()
            ledger_data = pickle.loads(serialized_data)
            
            # Import here to avoid circular dependency
            from venom.ledger.immutable_ledger import ImmutableLedger, LedgerEntry
            
            # Reconstruct ledger
            ledger = ImmutableLedger.__new__(ImmutableLedger)
            ledger.chain = []
            
            for entry_dict in ledger_data['chain']:
                entry = LedgerEntry(
                    index=entry_dict['index'],
                    timestamp=entry_dict['timestamp'],
                    data=entry_dict['data'],
                    previous_hash=entry_dict['previous_hash'],
                    hash=entry_dict['hash']
                )
                ledger.chain.append(entry)
            
            print(f"Restored ledger from s3://{self.bucket_name}/{backup_key}")
            print(f"Chain length: {len(ledger.chain)}")
            
            return ledger
            
        except ClientError as e:
            raise RuntimeError(f"Failed to restore ledger: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all ledger backups in S3
        
        Returns:
            List of backup information dictionaries
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.prefix
            )
            
            backups = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                
                # Get metadata
                metadata_response = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                
                backups.append({
                    'key': key,
                    'name': key.replace(self.prefix, ''),
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'metadata': metadata_response.get('Metadata', {}),
                    'version_id': metadata_response.get('VersionId')
                })
            
            # Sort by last modified (newest first)
            backups.sort(key=lambda x: x['last_modified'], reverse=True)
            
            return backups
            
        except ClientError as e:
            print(f"Error listing backups: {e}")
            return []
    
    def delete_backup(self, backup_key: str) -> bool:
        """
        Delete a backup from S3
        
        Args:
            backup_key: S3 key of the backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=backup_key
            )
            print(f"Deleted backup: {backup_key}")
            return True
            
        except ClientError as e:
            print(f"Error deleting backup: {e}")
            return False
    
    def get_backup_info(self, backup_key: str) -> Dict[str, Any]:
        """
        Get detailed information about a backup
        
        Args:
            backup_key: S3 key of the backup
            
        Returns:
            Backup information dictionary
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=backup_key
            )
            
            return {
                'key': backup_key,
                'name': backup_key.replace(self.prefix, ''),
                'size': response['ContentLength'],
                'last_modified': response['LastModified'].isoformat(),
                'etag': response['ETag'],
                'metadata': response.get('Metadata', {}),
                'version_id': response.get('VersionId'),
                'storage_class': response.get('StorageClass', 'STANDARD')
            }
            
        except ClientError as e:
            return {
                'error': str(e),
                'key': backup_key
            }
    
    def backup_state(
        self, 
        state_data: Dict[str, Any], 
        state_name: str
    ) -> str:
        """
        Backup arbitrary state data to S3
        
        Args:
            state_data: State dictionary to backup
            state_name: Name for the state backup
            
        Returns:
            S3 key of the backup
        """
        if not state_name.endswith('.json'):
            state_name += '.json'
        
        s3_key = self.prefix + 'state/' + state_name
        
        try:
            # Serialize to JSON
            json_data = json.dumps(state_data, indent=2)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'venom-type': 'state',
                    'timestamp': str(time.time())
                }
            )
            
            print(f"Backed up state to s3://{self.bucket_name}/{s3_key}")
            return s3_key
            
        except ClientError as e:
            raise RuntimeError(f"Failed to backup state: {e}")
    
    def restore_state(self, state_key: str) -> Dict[str, Any]:
        """
        Restore state data from S3
        
        Args:
            state_key: S3 key of the state backup
            
        Returns:
            Restored state dictionary
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=state_key
            )
            
            json_data = response['Body'].read().decode('utf-8')
            state_data = json.loads(json_data)
            
            print(f"Restored state from s3://{self.bucket_name}/{state_key}")
            return state_data
            
        except ClientError as e:
            raise RuntimeError(f"Failed to restore state: {e}")
