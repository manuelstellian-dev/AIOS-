"""
GCP Cloud Storage Backup Manager for VENOM Ω-AIOS
Backup and restore VENOM ledger/state to Google Cloud Storage
"""
import json
import pickle
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import VENOM version
try:
    from venom import __version__ as VENOM_VERSION
except ImportError:
    VENOM_VERSION = "0.2.0"

# Graceful imports
try:
    from google.cloud import storage
    from google.api_core.exceptions import GoogleAPIError, NotFound
    GCP_STORAGE_AVAILABLE = True
except ImportError:
    GCP_STORAGE_AVAILABLE = False
    storage = None
    GoogleAPIError = Exception
    NotFound = Exception


class StorageBackupManager:
    """
    Backup VENOM ledger and state to Google Cloud Storage
    
    Features:
    - Ledger backup/restore
    - Version management
    - Metadata tracking
    - Encryption support
    """
    
    def __init__(
        self, 
        bucket_name: str,
        project_id: str,
        prefix: str = 'venom-backups/'
    ):
        """
        Initialize GCS backup manager
        
        Args:
            bucket_name: GCS bucket name
            project_id: GCP project ID
            prefix: Object key prefix (default: venom-backups/)
        """
        if not GCP_STORAGE_AVAILABLE:
            raise ImportError(
                "Google Cloud Storage SDK is required for backup. "
                "Install with: pip install google-cloud-storage"
            )
        
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.prefix = prefix.rstrip('/') + '/'
        
        # Initialize storage client
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(bucket_name)
    
    def create_bucket(self, location: str = 'US') -> bool:
        """
        Create GCS bucket if it doesn't exist
        
        Args:
            location: Bucket location (default: US)
            
        Returns:
            True if successful or already exists, False otherwise
        """
        try:
            # Check if bucket exists
            if self.bucket.exists():
                print(f"Bucket {self.bucket_name} already exists")
                return True
            
            # Create bucket
            bucket = self.storage_client.create_bucket(
                self.bucket_name,
                location=location
            )
            
            # Enable versioning
            bucket.versioning_enabled = True
            bucket.patch()
            
            print(f"Created bucket: {self.bucket_name}")
            return True
            
        except GoogleAPIError as e:
            print(f"Error creating bucket: {e}")
            return False
    
    def backup_ledger(
        self, 
        ledger: 'ImmutableLedger', 
        backup_name: Optional[str] = None
    ) -> str:
        """
        Backup VENOM ledger to GCS
        
        Args:
            ledger: ImmutableLedger instance to backup
            backup_name: Optional custom backup name (default: timestamp-based)
            
        Returns:
            GCS object name of the backup
        """
        # Generate backup name if not provided
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_name = f"ledger-{timestamp}"
        
        # Add .pkl extension if not present
        if not backup_name.endswith('.pkl'):
            backup_name += '.pkl'
        
        object_name = self.prefix + backup_name
        
        try:
            # Serialize ledger
            ledger_data = {
                'chain': [entry.to_dict() for entry in ledger.chain],
                'version': VENOM_VERSION,
                'backup_timestamp': time.time(),
                'chain_length': len(ledger.chain)
            }
            
            # Convert to bytes
            serialized_data = pickle.dumps(ledger_data)
            
            # Create blob
            blob = self.bucket.blob(object_name)
            
            # Set metadata
            blob.metadata = {
                'venom-version': VENOM_VERSION,
                'chain-length': str(len(ledger.chain)),
                'backup-timestamp': str(time.time())
            }
            
            # Upload to GCS
            blob.upload_from_string(
                serialized_data,
                content_type='application/octet-stream'
            )
            
            print(f"Backed up ledger to gs://{self.bucket_name}/{object_name}")
            return object_name
            
        except GoogleAPIError as e:
            raise RuntimeError(f"Failed to backup ledger: {e}")
    
    def restore_ledger(self, blob_name: str) -> 'ImmutableLedger':
        """
        Restore VENOM ledger from GCS backup
        
        Args:
            blob_name: GCS object name of the backup
            
        Returns:
            Restored ImmutableLedger instance
        """
        try:
            # Download blob
            blob = self.bucket.blob(blob_name)
            serialized_data = blob.download_as_bytes()
            
            # Deserialize
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
            
            print(f"Restored ledger from gs://{self.bucket_name}/{blob_name}")
            print(f"Chain length: {len(ledger.chain)}")
            
            return ledger
            
        except GoogleAPIError as e:
            raise RuntimeError(f"Failed to restore ledger: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all ledger backups in GCS
        
        Returns:
            List of backup information dictionaries
        """
        try:
            blobs = self.bucket.list_blobs(prefix=self.prefix)
            
            backups = []
            for blob in blobs:
                backups.append({
                    'name': blob.name,
                    'full_name': blob.name,
                    'short_name': blob.name.replace(self.prefix, ''),
                    'size': blob.size,
                    'created': blob.time_created.isoformat() if blob.time_created else None,
                    'updated': blob.updated.isoformat() if blob.updated else None,
                    'metadata': blob.metadata or {},
                    'generation': blob.generation
                })
            
            # Sort by updated (newest first)
            backups.sort(
                key=lambda x: x['updated'] if x['updated'] else '', 
                reverse=True
            )
            
            return backups
            
        except GoogleAPIError as e:
            print(f"Error listing backups: {e}")
            return []
    
    def delete_backup(self, blob_name: str) -> bool:
        """
        Delete a backup from GCS
        
        Args:
            blob_name: GCS object name of the backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            
            print(f"Deleted backup: {blob_name}")
            return True
            
        except GoogleAPIError as e:
            print(f"Error deleting backup: {e}")
            return False
    
    def get_backup_info(self, blob_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a backup
        
        Args:
            blob_name: GCS object name of the backup
            
        Returns:
            Backup information dictionary
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.reload()  # Fetch latest metadata
            
            return {
                'name': blob.name,
                'size': blob.size,
                'created': blob.time_created.isoformat() if blob.time_created else None,
                'updated': blob.updated.isoformat() if blob.updated else None,
                'metadata': blob.metadata or {},
                'generation': blob.generation,
                'content_type': blob.content_type,
                'md5_hash': blob.md5_hash
            }
            
        except NotFound:
            return {
                'error': 'Backup not found',
                'name': blob_name
            }
        except GoogleAPIError as e:
            return {
                'error': str(e),
                'name': blob_name
            }
    
    def backup_state(
        self, 
        state_data: Dict[str, Any], 
        state_name: str
    ) -> str:
        """
        Backup arbitrary state data to GCS
        
        Args:
            state_data: State dictionary to backup
            state_name: Name for the state backup
            
        Returns:
            GCS object name of the backup
        """
        if not state_name.endswith('.json'):
            state_name += '.json'
        
        object_name = self.prefix + 'state/' + state_name
        
        try:
            # Serialize to JSON
            json_data = json.dumps(state_data, indent=2)
            
            # Create blob
            blob = self.bucket.blob(object_name)
            
            # Set metadata
            blob.metadata = {
                'venom-type': 'state',
                'timestamp': str(time.time())
            }
            
            # Upload to GCS
            blob.upload_from_string(
                json_data,
                content_type='application/json'
            )
            
            print(f"Backed up state to gs://{self.bucket_name}/{object_name}")
            return object_name
            
        except GoogleAPIError as e:
            raise RuntimeError(f"Failed to backup state: {e}")
    
    def restore_state(self, state_name: str) -> Dict[str, Any]:
        """
        Restore state data from GCS
        
        Args:
            state_name: GCS object name of the state backup
            
        Returns:
            Restored state dictionary
        """
        if not state_name.startswith(self.prefix + 'state/'):
            state_name = self.prefix + 'state/' + state_name
        
        try:
            blob = self.bucket.blob(state_name)
            json_data = blob.download_as_text()
            state_data = json.loads(json_data)
            
            print(f"Restored state from gs://{self.bucket_name}/{state_name}")
            return state_data
            
        except GoogleAPIError as e:
            raise RuntimeError(f"Failed to restore state: {e}")
