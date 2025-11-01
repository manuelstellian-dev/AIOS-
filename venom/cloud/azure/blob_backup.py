"""
Azure Blob Storage Backup Manager for VENOM Ω-AIOS
Backup and restore VENOM ledger/state to Azure Blob Storage
"""
import json
import pickle
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Graceful imports
try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False
    BlobServiceClient = None
    BlobClient = None
    ContainerClient = None
    ResourceExistsError = Exception
    ResourceNotFoundError = Exception


class BlobBackupManager:
    """
    Backup VENOM ledger and state to Azure Blob Storage
    
    Features:
    - Ledger backup/restore
    - Version management
    - Metadata tracking
    - Encryption support
    """
    
    def __init__(
        self, 
        account_name: str,
        container_name: str = 'venom-backups',
        account_key: Optional[str] = None,
        connection_string: Optional[str] = None
    ):
        """
        Initialize Azure Blob backup manager
        
        Args:
            account_name: Azure storage account name
            container_name: Blob container name (default: venom-backups)
            account_key: Storage account key (optional)
            connection_string: Connection string (optional)
        """
        if not AZURE_STORAGE_AVAILABLE:
            raise ImportError(
                "Azure Storage SDK is required for blob backup. "
                "Install with: pip install azure-storage-blob"
            )
        
        self.account_name = account_name
        self.container_name = container_name
        
        # Initialize blob service client
        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
        elif account_key:
            account_url = f"https://{account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=account_key
            )
        else:
            # Try DefaultAzureCredential
            try:
                from azure.identity import DefaultAzureCredential
                account_url = f"https://{account_name}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=DefaultAzureCredential()
                )
            except Exception as e:
                raise ValueError(
                    "Must provide either connection_string, account_key, "
                    "or have DefaultAzureCredential configured"
                )
        
        self.container_client = self.blob_service_client.get_container_client(
            container_name
        )
    
    def create_container(self) -> bool:
        """
        Create blob container if it doesn't exist
        
        Returns:
            True if successful or already exists, False otherwise
        """
        try:
            self.container_client.create_container()
            print(f"Created container: {self.container_name}")
            return True
            
        except ResourceExistsError:
            print(f"Container {self.container_name} already exists")
            return True
            
        except Exception as e:
            print(f"Error creating container: {e}")
            return False
    
    def backup_ledger(
        self, 
        ledger: 'ImmutableLedger', 
        backup_name: Optional[str] = None
    ) -> str:
        """
        Backup VENOM ledger to Azure Blob Storage
        
        Args:
            ledger: ImmutableLedger instance to backup
            backup_name: Optional custom backup name (default: timestamp-based)
            
        Returns:
            Blob name of the backup
        """
        # Generate backup name if not provided
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_name = f"ledger-{timestamp}"
        
        # Add .pkl extension if not present
        if not backup_name.endswith('.pkl'):
            backup_name += '.pkl'
        
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
                'venom_version': '0.2.0',
                'chain_length': str(len(ledger.chain)),
                'backup_timestamp': str(time.time())
            }
            
            # Upload to blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=backup_name
            )
            
            blob_client.upload_blob(
                serialized_data,
                overwrite=True,
                metadata=metadata
            )
            
            print(f"Backed up ledger to blob: {backup_name}")
            return backup_name
            
        except Exception as e:
            raise RuntimeError(f"Failed to backup ledger: {e}")
    
    def restore_ledger(self, blob_name: str) -> 'ImmutableLedger':
        """
        Restore VENOM ledger from Azure Blob backup
        
        Args:
            blob_name: Blob name of the backup
            
        Returns:
            Restored ImmutableLedger instance
        """
        try:
            # Download blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_data = blob_client.download_blob()
            serialized_data = blob_data.readall()
            
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
            
            print(f"Restored ledger from blob: {blob_name}")
            print(f"Chain length: {len(ledger.chain)}")
            
            return ledger
            
        except Exception as e:
            raise RuntimeError(f"Failed to restore ledger: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all ledger backups in blob container
        
        Returns:
            List of backup information dictionaries
        """
        try:
            blobs = self.container_client.list_blobs(include=['metadata'])
            
            backups = []
            for blob in blobs:
                backups.append({
                    'name': blob.name,
                    'size': blob.size,
                    'last_modified': blob.last_modified.isoformat(),
                    'metadata': blob.metadata or {},
                    'etag': blob.etag
                })
            
            # Sort by last modified (newest first)
            backups.sort(key=lambda x: x['last_modified'], reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    def delete_backup(self, blob_name: str) -> bool:
        """
        Delete a backup from blob storage
        
        Args:
            blob_name: Blob name of the backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            
            print(f"Deleted backup: {blob_name}")
            return True
            
        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False
    
    def get_backup_info(self, blob_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a backup
        
        Args:
            blob_name: Blob name of the backup
            
        Returns:
            Backup information dictionary
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            properties = blob_client.get_blob_properties()
            
            return {
                'name': blob_name,
                'size': properties.size,
                'last_modified': properties.last_modified.isoformat(),
                'etag': properties.etag,
                'metadata': properties.metadata or {},
                'content_type': properties.content_settings.content_type,
                'blob_type': properties.blob_type
            }
            
        except Exception as e:
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
        Backup arbitrary state data to blob storage
        
        Args:
            state_data: State dictionary to backup
            state_name: Name for the state backup
            
        Returns:
            Blob name of the backup
        """
        if not state_name.endswith('.json'):
            state_name += '.json'
        
        blob_name = f"state/{state_name}"
        
        try:
            # Serialize to JSON
            json_data = json.dumps(state_data, indent=2)
            
            # Upload to blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(
                json_data.encode('utf-8'),
                overwrite=True,
                metadata={
                    'venom_type': 'state',
                    'timestamp': str(time.time())
                }
            )
            
            print(f"Backed up state to blob: {blob_name}")
            return blob_name
            
        except Exception as e:
            raise RuntimeError(f"Failed to backup state: {e}")
    
    def restore_state(self, state_name: str) -> Dict[str, Any]:
        """
        Restore state data from blob storage
        
        Args:
            state_name: Blob name of the state backup
            
        Returns:
            Restored state dictionary
        """
        if not state_name.startswith('state/'):
            state_name = f"state/{state_name}"
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=state_name
            )
            
            blob_data = blob_client.download_blob()
            json_data = blob_data.readall().decode('utf-8')
            state_data = json.loads(json_data)
            
            print(f"Restored state from blob: {state_name}")
            return state_data
            
        except Exception as e:
            raise RuntimeError(f"Failed to restore state: {e}")
