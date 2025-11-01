"""
Azure AKS Deployer for VENOM Ω-AIOS
Deploy VENOM to Azure Kubernetes Service
"""
import time
from typing import Dict, List, Any, Optional

# Graceful imports
try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.containerservice import ContainerServiceClient
    from azure.mgmt.containerservice.models import (
        ManagedCluster,
        ManagedClusterAgentPoolProfile,
        ContainerServiceLinuxProfile,
        ContainerServiceSshConfiguration,
        ContainerServiceSshPublicKey
    )
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    DefaultAzureCredential = None
    ContainerServiceClient = None

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    client = None
    config = None
    ApiException = Exception


class AKSDeployer:
    """
    Deploy VENOM to Azure AKS (Azure Kubernetes Service)
    
    Supports:
    - AKS cluster creation with managed identity
    - VENOM container deployment
    - Auto-scaling configuration
    - Health monitoring
    """
    
    def __init__(
        self, 
        resource_group: str,
        cluster_name: str = 'venom-cluster', 
        location: str = 'eastus',
        subscription_id: Optional[str] = None
    ):
        """
        Initialize AKS deployer
        
        Args:
            resource_group: Azure resource group name
            cluster_name: Name for the AKS cluster
            location: Azure region (default: eastus)
            subscription_id: Azure subscription ID (optional)
        """
        if not AZURE_AVAILABLE:
            raise ImportError(
                "Azure SDK is required for AKS deployment. "
                "Install with: pip install azure-mgmt-containerservice azure-identity"
            )
        
        self.resource_group = resource_group
        self.cluster_name = cluster_name
        self.location = location
        
        # Initialize Azure clients
        self.credential = DefaultAzureCredential()
        
        if subscription_id:
            self.aks_client = ContainerServiceClient(
                credential=self.credential,
                subscription_id=subscription_id
            )
        else:
            # Try to get subscription from environment
            try:
                import os
                sub_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
                if not sub_id:
                    raise ValueError("AZURE_SUBSCRIPTION_ID must be set")
                self.aks_client = ContainerServiceClient(
                    credential=self.credential,
                    subscription_id=sub_id
                )
            except Exception as e:
                raise ValueError(f"Cannot determine subscription ID: {e}")
    
    def create_cluster(
        self, 
        node_count: int = 3, 
        vm_size: str = 'Standard_DS2_v2'
    ) -> Dict[str, Any]:
        """
        Create AKS cluster with managed identity
        
        Args:
            node_count: Number of worker nodes (default: 3)
            vm_size: Azure VM size (default: Standard_DS2_v2)
            
        Returns:
            Cluster information dictionary
        """
        try:
            # Define agent pool
            agent_pool_profile = ManagedClusterAgentPoolProfile(
                name='nodepool1',
                count=node_count,
                vm_size=vm_size,
                os_type='Linux',
                mode='System',
                enable_auto_scaling=True,
                min_count=1,
                max_count=node_count * 2
            )
            
            # Define cluster parameters
            managed_cluster = ManagedCluster(
                location=self.location,
                dns_prefix=self.cluster_name,
                agent_pool_profiles=[agent_pool_profile],
                identity={
                    'type': 'SystemAssigned'
                },
                network_profile={
                    'network_plugin': 'kubenet',
                    'load_balancer_sku': 'standard'
                }
            )
            
            # Create cluster
            print(f"Creating AKS cluster '{self.cluster_name}'...")
            poller = self.aks_client.managed_clusters.begin_create_or_update(
                resource_group_name=self.resource_group,
                resource_name=self.cluster_name,
                parameters=managed_cluster
            )
            
            # Wait for completion
            cluster = poller.result()
            
            return {
                'cluster_name': cluster.name,
                'location': cluster.location,
                'status': cluster.provisioning_state,
                'fqdn': cluster.fqdn,
                'kubernetes_version': cluster.kubernetes_version,
                'node_count': node_count,
                'vm_size': vm_size
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'cluster_name': self.cluster_name,
                'status': 'FAILED'
            }
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get AKS cluster information
        
        Returns:
            Cluster details dictionary
        """
        try:
            cluster = self.aks_client.managed_clusters.get(
                resource_group_name=self.resource_group,
                resource_name=self.cluster_name
            )
            
            return {
                'cluster_name': cluster.name,
                'status': cluster.provisioning_state,
                'location': cluster.location,
                'fqdn': cluster.fqdn,
                'kubernetes_version': cluster.kubernetes_version,
                'node_resource_group': cluster.node_resource_group,
                'id': cluster.id
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'cluster_name': self.cluster_name
            }
    
    def deploy_venom(
        self, 
        image: str = 'venom-omega:latest', 
        replicas: int = 3
    ) -> Dict[str, Any]:
        """
        Deploy VENOM containers to AKS cluster
        
        Args:
            image: Docker image to deploy
            replicas: Number of replicas
            
        Returns:
            Deployment information
        """
        if not KUBERNETES_AVAILABLE:
            return {
                'error': 'kubernetes library not available',
                'message': 'Install with: pip install kubernetes'
            }
        
        try:
            # Get AKS credentials
            self._configure_kubectl()
            
            # Create Kubernetes API client
            apps_v1 = client.AppsV1Api()
            core_v1 = client.CoreV1Api()
            
            # Define deployment
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name="venom-deployment"),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(
                        match_labels={"app": "venom"}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": "venom"}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="venom",
                                    image=image,
                                    ports=[client.V1ContainerPort(container_port=8080)],
                                    resources=client.V1ResourceRequirements(
                                        requests={"memory": "512Mi", "cpu": "250m"},
                                        limits={"memory": "1Gi", "cpu": "500m"}
                                    )
                                )
                            ]
                        )
                    )
                )
            )
            
            # Create deployment
            apps_v1.create_namespaced_deployment(
                namespace="default",
                body=deployment
            )
            
            # Create service
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name="venom-service"),
                spec=client.V1ServiceSpec(
                    type="LoadBalancer",
                    selector={"app": "venom"},
                    ports=[client.V1ServicePort(port=80, target_port=8080)]
                )
            )
            
            core_v1.create_namespaced_service(
                namespace="default",
                body=service
            )
            
            return {
                'deployment': 'venom-deployment',
                'service': 'venom-service',
                'replicas': replicas,
                'image': image,
                'status': 'deployed'
            }
            
        except ApiException as e:
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def scale_deployment(self, replicas: int) -> Dict[str, Any]:
        """
        Scale VENOM deployment
        
        Args:
            replicas: Target number of replicas
            
        Returns:
            Scaling result
        """
        if not KUBERNETES_AVAILABLE:
            return {
                'error': 'kubernetes library not available'
            }
        
        try:
            self._configure_kubectl()
            apps_v1 = client.AppsV1Api()
            
            # Update deployment scale
            apps_v1.patch_namespaced_deployment_scale(
                name="venom-deployment",
                namespace="default",
                body={"spec": {"replicas": replicas}}
            )
            
            return {
                'deployment': 'venom-deployment',
                'replicas': replicas,
                'status': 'scaled'
            }
            
        except ApiException as e:
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def get_pods_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all VENOM pods
        
        Returns:
            List of pod status dictionaries
        """
        if not KUBERNETES_AVAILABLE:
            return [{'error': 'kubernetes library not available'}]
        
        try:
            self._configure_kubectl()
            core_v1 = client.CoreV1Api()
            
            pods = core_v1.list_namespaced_pod(
                namespace="default",
                label_selector="app=venom"
            )
            
            pod_status = []
            for pod in pods.items:
                pod_status.append({
                    'name': pod.metadata.name,
                    'status': pod.status.phase,
                    'ready': all(c.ready for c in pod.status.container_statuses or []),
                    'restart_count': sum(c.restart_count for c in pod.status.container_statuses or []),
                    'node': pod.spec.node_name
                })
            
            return pod_status
            
        except ApiException as e:
            return [{'error': str(e)}]
    
    def delete_cluster(self) -> bool:
        """
        Delete AKS cluster and all resources
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Deleting AKS cluster '{self.cluster_name}'...")
            poller = self.aks_client.managed_clusters.begin_delete(
                resource_group_name=self.resource_group,
                resource_name=self.cluster_name
            )
            
            # Wait for deletion
            poller.result()
            print(f"Cluster {self.cluster_name} deleted successfully")
            return True
            
        except Exception as e:
            print(f"Error deleting cluster: {e}")
            return False
    
    # Helper methods
    
    def _configure_kubectl(self):
        """Configure kubectl for AKS cluster"""
        # Get AKS credentials
        credentials = self.aks_client.managed_clusters.list_cluster_user_credentials(
            resource_group_name=self.resource_group,
            resource_name=self.cluster_name
        )
        
        # Get the kubeconfig
        kubeconfig_data = credentials.kubeconfigs[0].value
        
        # Load kubeconfig
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as f:
            f.write(kubeconfig_data)
            kubeconfig_path = f.name
        
        config.load_kube_config(config_file=kubeconfig_path)
