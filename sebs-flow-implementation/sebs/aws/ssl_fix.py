"""
SSL fix helper for AWS Academy environments.
"""
import os
import urllib3
import boto3
import botocore.config

# Disable SSL warnings for AWS Academy environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_boto3_client(service_name, session=None, **kwargs):
    """Create a boto3 client with SSL error handling for AWS Academy environments."""
    
    config = botocore.config.Config(
        retries={'max_attempts': 3},
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    )
    
    client_kwargs = {'config': config, **kwargs}
    
    try:
        if session:
            client = session.client(service_name, **client_kwargs)
        else:
            client = boto3.client(service_name, **client_kwargs)
        
        # Test the client with a simple operation
        if service_name == 'sts':
            client.get_caller_identity()
        elif service_name == 'iam':
            try:
                client.get_user()
            except:
                pass  # get_user might fail due to permissions, but that's okay
                
        return client
    except Exception as e:
        if "certificate" in str(e).lower() or "ssl" in str(e).lower():
            # AWS Academy SSL issue - disable verification
            client_kwargs['verify'] = False
            if session:
                client = session.client(service_name, **client_kwargs)
            else:
                client = boto3.client(service_name, **client_kwargs)
            return client
        else:
            raise e