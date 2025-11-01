"""
AWS EKS Deployer for VENOM Ω-AIOS
Deploy VENOM to Amazon Elastic Kubernetes Service
"""
import json
import time
import base64
from typing import Dict, List, Any, Optional

# Graceful imports
try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    ClientError = Exception
    BotoCoreError = Exception

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    client = None
    config = None
    ApiException = Exception


class EKSDeployer:
    """
    Deploy VENOM to AWS EKS (Elastic Kubernetes Service)
    
    Supports:
    - EKS cluster creation
    - VENOM container deployment
    - Auto-scaling configuration
    - Health monitoring
    """
    
    def __init__(self, region: str = 'us-east-1', cluster_name: str = 'venom-cluster'):
        """
        Initialize EKS deployer
        
        Args:
            region: AWS region (default: us-east-1)
            cluster_name: Name for the EKS cluster
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for AWS EKS deployment. "
                "Install with: pip install boto3"
            )
        
        self.region = region
        self.cluster_name = cluster_name
        self.eks_client = boto3.client('eks', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_cluster(
        self, 
        node_count: int = 3, 
        instance_type: str = 't3.medium'
    ) -> Dict[str, Any]:
        """
        Create EKS cluster with managed node group
        
        Args:
            node_count: Number of worker nodes (default: 3)
            instance_type: EC2 instance type (default: t3.medium)
            
        Returns:
            Cluster information dictionary
        """
        try:
            # Get default VPC and subnets
            vpc_id = self._get_default_vpc()
            subnet_ids = self._get_vpc_subnets(vpc_id)
            
            # Create or get cluster role
            cluster_role_arn = self._ensure_cluster_role()
            
            # Create security group
            security_group_id = self._create_security_group(vpc_id)
            
            # Create EKS cluster
            cluster_response = self.eks_client.create_cluster(
                name=self.cluster_name,
                version='1.28',
                roleArn=cluster_role_arn,
                resourcesVpcConfig={
                    'subnetIds': subnet_ids[:2],  # Use first 2 subnets
                    'securityGroupIds': [security_group_id],
                    'endpointPublicAccess': True,
                    'endpointPrivateAccess': False
                }
            )
            
            # Wait for cluster to become active
            print(f"Creating EKS cluster '{self.cluster_name}'...")
            self._wait_for_cluster_active()
            
            # Create node group
            node_role_arn = self._ensure_node_role()
            self._create_node_group(
                subnet_ids=subnet_ids,
                instance_type=instance_type,
                node_count=node_count,
                node_role_arn=node_role_arn
            )
            
            return {
                'cluster_name': self.cluster_name,
                'region': self.region,
                'status': 'ACTIVE',
                'endpoint': cluster_response['cluster']['endpoint'],
                'vpc_id': vpc_id,
                'node_count': node_count,
                'instance_type': instance_type
            }
            
        except ClientError as e:
            return {
                'error': str(e),
                'cluster_name': self.cluster_name,
                'status': 'FAILED'
            }
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get EKS cluster information
        
        Returns:
            Cluster details dictionary
        """
        try:
            response = self.eks_client.describe_cluster(name=self.cluster_name)
            cluster = response['cluster']
            
            return {
                'cluster_name': cluster['name'],
                'status': cluster['status'],
                'endpoint': cluster.get('endpoint'),
                'version': cluster['version'],
                'created_at': cluster['createdAt'].isoformat(),
                'arn': cluster['arn']
            }
        except ClientError as e:
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
        Deploy VENOM containers to EKS cluster
        
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
        Delete EKS cluster and all resources
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete node groups first
            nodegroups = self.eks_client.list_nodegroups(
                clusterName=self.cluster_name
            )
            
            for ng in nodegroups.get('nodegroups', []):
                self.eks_client.delete_nodegroup(
                    clusterName=self.cluster_name,
                    nodegroupName=ng
                )
                print(f"Deleting node group: {ng}")
            
            # Wait for node groups to delete
            time.sleep(30)
            
            # Delete cluster
            self.eks_client.delete_cluster(name=self.cluster_name)
            print(f"Deleting cluster: {self.cluster_name}")
            
            return True
            
        except ClientError as e:
            print(f"Error deleting cluster: {e}")
            return False
    
    # Helper methods
    
    def _get_default_vpc(self) -> str:
        """Get default VPC ID"""
        vpcs = self.ec2_client.describe_vpcs(
            Filters=[{'Name': 'isDefault', 'Values': ['true']}]
        )
        if vpcs['Vpcs']:
            return vpcs['Vpcs'][0]['VpcId']
        raise ValueError("No default VPC found")
    
    def _get_vpc_subnets(self, vpc_id: str) -> List[str]:
        """Get subnet IDs for VPC"""
        subnets = self.ec2_client.describe_subnets(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
        )
        return [s['SubnetId'] for s in subnets['Subnets']]
    
    def _ensure_cluster_role(self) -> str:
        """Create or get EKS cluster IAM role"""
        role_name = f"{self.cluster_name}-cluster-role"
        
        try:
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
        except ClientError:
            # Create role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "eks.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            # Attach policies
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
            )
            
            return response['Role']['Arn']
    
    def _ensure_node_role(self) -> str:
        """Create or get EKS node IAM role"""
        role_name = f"{self.cluster_name}-node-role"
        
        try:
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
        except ClientError:
            # Create role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
                "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            return response['Role']['Arn']
    
    def _create_security_group(self, vpc_id: str) -> str:
        """Create security group for EKS"""
        try:
            response = self.ec2_client.create_security_group(
                GroupName=f"{self.cluster_name}-sg",
                Description="Security group for VENOM EKS cluster",
                VpcId=vpc_id
            )
            return response['GroupId']
        except ClientError as e:
            if 'already exists' in str(e):
                # Get existing security group
                sgs = self.ec2_client.describe_security_groups(
                    Filters=[
                        {'Name': 'group-name', 'Values': [f"{self.cluster_name}-sg"]},
                        {'Name': 'vpc-id', 'Values': [vpc_id]}
                    ]
                )
                if sgs['SecurityGroups']:
                    return sgs['SecurityGroups'][0]['GroupId']
            raise
    
    def _wait_for_cluster_active(self, timeout: int = 900):
        """Wait for cluster to become active"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.eks_client.describe_cluster(name=self.cluster_name)
            status = response['cluster']['status']
            
            if status == 'ACTIVE':
                print(f"Cluster {self.cluster_name} is ACTIVE")
                return
            elif status == 'FAILED':
                raise RuntimeError(f"Cluster creation failed")
            
            time.sleep(30)
        
        raise TimeoutError(f"Cluster did not become active within {timeout} seconds")
    
    def _create_node_group(
        self, 
        subnet_ids: List[str],
        instance_type: str,
        node_count: int,
        node_role_arn: str
    ):
        """Create managed node group"""
        nodegroup_name = f"{self.cluster_name}-nodes"
        
        self.eks_client.create_nodegroup(
            clusterName=self.cluster_name,
            nodegroupName=nodegroup_name,
            scalingConfig={
                'minSize': 1,
                'maxSize': node_count * 2,
                'desiredSize': node_count
            },
            subnets=subnet_ids,
            instanceTypes=[instance_type],
            amiType='AL2_x86_64',
            nodeRole=node_role_arn
        )
        
        print(f"Creating node group '{nodegroup_name}'...")
    
    def _configure_kubectl(self):
        """Configure kubectl for EKS cluster"""
        # Get cluster info
        cluster_info = self.eks_client.describe_cluster(name=self.cluster_name)
        cluster = cluster_info['cluster']
        
        # Create kubeconfig
        kubeconfig = {
            'apiVersion': 'v1',
            'kind': 'Config',
            'clusters': [{
                'name': self.cluster_name,
                'cluster': {
                    'server': cluster['endpoint'],
                    'certificate-authority-data': cluster['certificateAuthority']['data']
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
                        'command': 'aws',
                        'args': [
                            'eks', 'get-token',
                            '--cluster-name', self.cluster_name,
                            '--region', self.region
                        ]
                    }
                }
            }]
        }
        
        # Load kubeconfig
        config.load_kube_config_from_dict(kubeconfig)
