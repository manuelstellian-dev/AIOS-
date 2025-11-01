"""
GCP GKE Deployer for VENOM Ω-AIOS
Deploy VENOM to Google Kubernetes Engine
"""
import time
from typing import Dict, List, Any, Optional

# Graceful imports
try:
    from google.cloud import container_v1
    from google.api_core.exceptions import GoogleAPIError, NotFound
    GCP_CONTAINER_AVAILABLE = True
except ImportError:
    GCP_CONTAINER_AVAILABLE = False
    container_v1 = None
    GoogleAPIError = Exception
    NotFound = Exception

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    client = None
    config = None
    ApiException = Exception


class GKEDeployer:
    """
    Deploy VENOM to GCP GKE (Google Kubernetes Engine)
    
    Supports:
    - GKE cluster creation (standard/autopilot)
    - VENOM container deployment
    - Auto-scaling configuration
    - Health monitoring
    """
    
    def __init__(
        self, 
        project_id: str,
        cluster_name: str = 'venom-cluster', 
        zone: str = 'us-central1-a'
    ):
        """
        Initialize GKE deployer
        
        Args:
            project_id: GCP project ID
            cluster_name: Name for the GKE cluster
            zone: GCP zone (default: us-central1-a)
        """
        if not GCP_CONTAINER_AVAILABLE:
            raise ImportError(
                "Google Cloud Container SDK is required for GKE deployment. "
                "Install with: pip install google-cloud-container"
            )
        
        self.project_id = project_id
        self.cluster_name = cluster_name
        self.zone = zone
        self.location = zone  # Can also be region for regional clusters
        
        # Initialize GKE client
        self.cluster_manager = container_v1.ClusterManagerClient()
        self.parent = f"projects/{project_id}/locations/{zone}"
    
    def create_cluster(
        self, 
        node_count: int = 3, 
        machine_type: str = 'e2-medium'
    ) -> Dict[str, Any]:
        """
        Create GKE cluster
        
        Args:
            node_count: Number of worker nodes (default: 3)
            machine_type: GCE machine type (default: e2-medium)
            
        Returns:
            Cluster information dictionary
        """
        try:
            # Define cluster configuration
            cluster = container_v1.Cluster(
                name=self.cluster_name,
                initial_node_count=node_count,
                node_config=container_v1.NodeConfig(
                    machine_type=machine_type,
                    disk_size_gb=100,
                    oauth_scopes=[
                        "https://www.googleapis.com/auth/compute",
                        "https://www.googleapis.com/auth/devstorage.read_only",
                        "https://www.googleapis.com/auth/logging.write",
                        "https://www.googleapis.com/auth/monitoring"
                    ]
                ),
                addons_config=container_v1.AddonsConfig(
                    http_load_balancing=container_v1.HttpLoadBalancing(disabled=False),
                    horizontal_pod_autoscaling=container_v1.HorizontalPodAutoscaling(disabled=False)
                ),
                autoscaling=container_v1.ClusterAutoscaling(
                    enable_node_autoprovisioning=False
                )
            )
            
            # Create cluster request
            request = container_v1.CreateClusterRequest(
                parent=self.parent,
                cluster=cluster
            )
            
            print(f"Creating GKE cluster '{self.cluster_name}'...")
            operation = self.cluster_manager.create_cluster(request=request)
            
            # Wait for operation to complete
            self._wait_for_operation(operation)
            
            # Get cluster info
            cluster_info = self.get_cluster_info()
            
            return {
                'cluster_name': self.cluster_name,
                'project_id': self.project_id,
                'zone': self.zone,
                'status': 'RUNNING',
                'endpoint': cluster_info.get('endpoint'),
                'node_count': node_count,
                'machine_type': machine_type
            }
            
        except GoogleAPIError as e:
            return {
                'error': str(e),
                'cluster_name': self.cluster_name,
                'status': 'FAILED'
            }
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get GKE cluster information
        
        Returns:
            Cluster details dictionary
        """
        try:
            cluster_path = f"{self.parent}/clusters/{self.cluster_name}"
            
            request = container_v1.GetClusterRequest(name=cluster_path)
            cluster = self.cluster_manager.get_cluster(request=request)
            
            return {
                'cluster_name': cluster.name,
                'status': cluster.status.name,
                'endpoint': cluster.endpoint,
                'current_node_count': cluster.current_node_count,
                'location': cluster.location,
                'self_link': cluster.self_link
            }
            
        except NotFound:
            return {
                'error': 'Cluster not found',
                'cluster_name': self.cluster_name
            }
        except GoogleAPIError as e:
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
        Deploy VENOM containers to GKE cluster
        
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
            # Configure kubectl
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
        Delete GKE cluster and all resources
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cluster_path = f"{self.parent}/clusters/{self.cluster_name}"
            
            request = container_v1.DeleteClusterRequest(name=cluster_path)
            
            print(f"Deleting GKE cluster '{self.cluster_name}'...")
            operation = self.cluster_manager.delete_cluster(request=request)
            
            # Wait for deletion
            self._wait_for_operation(operation)
            
            print(f"Cluster {self.cluster_name} deleted successfully")
            return True
            
        except GoogleAPIError as e:
            print(f"Error deleting cluster: {e}")
            return False
    
    # Helper methods
    
    def _wait_for_operation(self, operation, timeout: int = 900):
        """Wait for GKE operation to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            op_request = container_v1.GetOperationRequest(
                name=operation.self_link
            )
            
            op_result = self.cluster_manager.get_operation(request=op_request)
            
            if op_result.status == container_v1.Operation.Status.DONE:
                print(f"Operation completed successfully")
                return
            elif op_result.status == container_v1.Operation.Status.ABORTING:
                raise RuntimeError(f"Operation aborted")
            
            time.sleep(30)
        
        raise TimeoutError(f"Operation did not complete within {timeout} seconds")
    
    def _configure_kubectl(self):
        """Configure kubectl for GKE cluster"""
        # Get cluster info
        cluster_path = f"{self.parent}/clusters/{self.cluster_name}"
        request = container_v1.GetClusterRequest(name=cluster_path)
        cluster = self.cluster_manager.get_cluster(request=request)
        
        # Create kubeconfig
        import base64
        
        kubeconfig = {
            'apiVersion': 'v1',
            'kind': 'Config',
            'clusters': [{
                'name': self.cluster_name,
                'cluster': {
                    'server': f"https://{cluster.endpoint}",
                    'certificate-authority-data': cluster.master_auth.cluster_ca_certificate
                }
            }],
            'contexts': [{
                'name': self.cluster_name,
                'context': {
                    'cluster': self.cluster_name,
                    'user': self.cluster_name
                }
            }],
            'current-context': self.cluster_name,
            'users': [{
                'name': self.cluster_name,
                'user': {
                    'exec': {
                        'apiVersion': 'client.authentication.k8s.io/v1beta1',
                        'command': 'gcloud',
                        'args': [
                            'container', 'clusters', 'get-credentials',
                            self.cluster_name,
                            '--zone', self.zone,
                            '--project', self.project_id
                        ]
                    }
                }
            }]
        }
        
        # Load kubeconfig
        config.load_kube_config_from_dict(kubeconfig)
