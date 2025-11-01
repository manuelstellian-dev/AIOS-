"""
AWS Lambda Handler for VENOM Ω-AIOS
Serverless execution wrapper for VENOM operations
"""
import json
import time
from typing import Dict, Any, Optional

# Graceful imports
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    ClientError = Exception


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda entry point for VENOM Ω-AIOS
    
    Event structure:
    {
        "action": "execute_wave" | "health_check" | "benchmark",
        "wave_config": {...},
        "params": {...}
    }
    
    Args:
        event: Lambda event dictionary
        context: Lambda context object
        
    Returns:
        Response dictionary with results
    """
    try:
        action = event.get('action', 'health_check')
        
        if action == 'health_check':
            return _health_check(event, context)
        elif action == 'execute_wave':
            return _execute_wave(event, context)
        elif action == 'benchmark':
            return _benchmark(event, context)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Unknown action: {action}',
                    'valid_actions': ['health_check', 'execute_wave', 'benchmark']
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'error_type': type(e).__name__
            })
        }


def _health_check(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Perform health check
    
    Returns:
        Health status
    """
    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'healthy',
            'service': 'VENOM Ω-AIOS Lambda',
            'timestamp': time.time(),
            'request_id': context.request_id if context else 'local'
        })
    }


def _execute_wave(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Execute VENOM wave configuration
    
    Args:
        event: Must contain 'wave_config' with wave parameters
        context: Lambda context
        
    Returns:
        Execution results
    """
    wave_config = event.get('wave_config', {})
    
    if not wave_config:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Missing wave_config in event'
            })
        }
    
    # Simulate wave execution (in real implementation, would use VENOM core)
    wave_type = wave_config.get('type', 'standard')
    iterations = wave_config.get('iterations', 10)
    
    results = {
        'wave_type': wave_type,
        'iterations': iterations,
        'status': 'completed',
        'execution_time_ms': 42.11,  # Placeholder
        'timestamp': time.time()
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }


def _benchmark(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Run VENOM benchmark
    
    Args:
        event: Benchmark parameters
        context: Lambda context
        
    Returns:
        Benchmark results
    """
    params = event.get('params', {})
    test_type = params.get('test_type', 'inference')
    
    # Simulate benchmark (in real implementation, would use VENOM benchmark)
    results = {
        'test_type': test_type,
        'throughput': 1000.0,  # ops/sec
        'latency_ms': 5.2,
        'status': 'completed',
        'timestamp': time.time()
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }


class LambdaDeployer:
    """
    Deploy and manage AWS Lambda functions for VENOM
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize Lambda deployer
        
        Args:
            region: AWS region
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for AWS Lambda deployment. "
                "Install with: pip install boto3"
            )
        
        self.region = region
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
    
    def create_function(
        self, 
        function_name: str, 
        runtime: str = 'python3.11',
        handler: str = 'lambda_handler.lambda_handler',
        memory_size: int = 512,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Create Lambda function
        
        Args:
            function_name: Name for the Lambda function
            runtime: Lambda runtime (default: python3.11)
            handler: Handler function path
            memory_size: Memory in MB (default: 512)
            timeout: Timeout in seconds (default: 300)
            
        Returns:
            Function creation response
        """
        try:
            # Get or create execution role
            role_arn = self._ensure_lambda_role(function_name)
            
            # Create function (with placeholder code)
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime=runtime,
                Role=role_arn,
                Handler=handler,
                Code={
                    'ZipFile': self._get_placeholder_code()
                },
                Description='VENOM Ω-AIOS Lambda Function',
                Timeout=timeout,
                MemorySize=memory_size,
                Environment={
                    'Variables': {
                        'VENOM_MODE': 'lambda',
                        'VENOM_VERSION': '0.2.0'
                    }
                }
            )
            
            return {
                'function_name': response['FunctionName'],
                'function_arn': response['FunctionArn'],
                'runtime': response['Runtime'],
                'status': 'created',
                'memory_size': response['MemorySize'],
                'timeout': response['Timeout']
            }
            
        except ClientError as e:
            return {
                'error': str(e),
                'function_name': function_name,
                'status': 'failed'
            }
    
    def update_code(
        self, 
        function_name: str, 
        zip_file: bytes
    ) -> Dict[str, Any]:
        """
        Update Lambda function code
        
        Args:
            function_name: Lambda function name
            zip_file: ZIP file bytes containing function code
            
        Returns:
            Update response
        """
        try:
            response = self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_file
            )
            
            return {
                'function_name': response['FunctionName'],
                'version': response['Version'],
                'status': 'updated',
                'code_size': response['CodeSize']
            }
            
        except ClientError as e:
            return {
                'error': str(e),
                'function_name': function_name,
                'status': 'failed'
            }
    
    def invoke(
        self, 
        function_name: str, 
        payload: Dict[str, Any],
        invocation_type: str = 'RequestResponse'
    ) -> Dict[str, Any]:
        """
        Invoke Lambda function
        
        Args:
            function_name: Lambda function name
            payload: Event payload dictionary
            invocation_type: 'RequestResponse' (sync) or 'Event' (async)
            
        Returns:
            Invocation response
        """
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(payload).encode('utf-8')
            )
            
            # Parse response
            response_payload = json.loads(
                response['Payload'].read().decode('utf-8')
            )
            
            return {
                'function_name': function_name,
                'status_code': response['StatusCode'],
                'execution_result': response_payload,
                'request_id': response.get('ResponseMetadata', {}).get('RequestId')
            }
            
        except ClientError as e:
            return {
                'error': str(e),
                'function_name': function_name,
                'status': 'failed'
            }
    
    def delete_function(self, function_name: str) -> bool:
        """
        Delete Lambda function
        
        Args:
            function_name: Lambda function name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.lambda_client.delete_function(FunctionName=function_name)
            print(f"Deleted Lambda function: {function_name}")
            return True
            
        except ClientError as e:
            print(f"Error deleting function: {e}")
            return False
    
    def get_function_info(self, function_name: str) -> Dict[str, Any]:
        """
        Get Lambda function information
        
        Args:
            function_name: Lambda function name
            
        Returns:
            Function information dictionary
        """
        try:
            response = self.lambda_client.get_function(
                FunctionName=function_name
            )
            
            config = response['Configuration']
            
            return {
                'function_name': config['FunctionName'],
                'function_arn': config['FunctionArn'],
                'runtime': config['Runtime'],
                'handler': config['Handler'],
                'memory_size': config['MemorySize'],
                'timeout': config['Timeout'],
                'last_modified': config['LastModified'],
                'code_size': config['CodeSize'],
                'state': config['State']
            }
            
        except ClientError as e:
            return {
                'error': str(e),
                'function_name': function_name
            }
    
    # Helper methods
    
    def _ensure_lambda_role(self, function_name: str) -> str:
        """Create or get Lambda execution role"""
        role_name = f"{function_name}-lambda-role"
        
        try:
            response = self.iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
        except ClientError:
            # Create role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"Execution role for {function_name}"
            )
            
            # Attach basic execution policy
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            )
            
            # Wait for role to propagate
            time.sleep(10)
            
            return response['Role']['Arn']
    
    def _get_placeholder_code(self) -> bytes:
        """Get placeholder Lambda code"""
        code = '''
import json

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'VENOM Lambda placeholder',
            'event': event
        })
    }
'''
        import zipfile
        import io
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_handler.py', code)
        
        return zip_buffer.getvalue()
