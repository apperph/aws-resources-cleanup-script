import boto3
from datetime import datetime, timezone, timedelta

def delete_old_ecr_repositories(event, context):
    account_ids = ['707125572044', '058690268851', '584782747967', '236921907600', '562032292525']  # Add more account IDs as needed

    for account_id in account_ids:
        # Assume the role in the target account
        sts = boto3.client('sts')
        assumed_role = sts.assume_role(
            RoleArn=f'arn:aws:iam::{account_id}:role/LambdaCostOptimization',
            RoleSessionName='AssumedRoleSession'
        )
        
        # Extract temporary credentials
        credentials = assumed_role['Credentials']

        regions = ['ap-southeast-1','ap-southeast-2','us-east-1','us-east-2','us-west-2']

        for region in regions:
            # print(f"Checking region: {region}")
            ecr_client = boto3.client('ecr', region_name=region,
                                      aws_access_key_id=credentials['AccessKeyId'],
                                      aws_secret_access_key=credentials['SecretAccessKey'],
                                      aws_session_token=credentials['SessionToken'])
    
            # Get a list of all ECR repositories in the specified region
            repositories_response = ecr_client.describe_repositories()
            repositories = repositories_response['repositories']
            
            # Iterate over each repository and delete it if it's older than 5 days
            for repository in repositories:
                repository_name = repository['repositoryName']
                created_at = repository['createdAt']
                
                if created_at:
                    repo_age = datetime.now(timezone.utc) - created_at
                    if repo_age > timedelta(days=5):
                        print(f"Deleting ECR repository: {repository_name} (Age: {repo_age})")
                        ecr_client.delete_repository(repositoryName=repository_name, force=True)
                    else:
                        print(f"Skipping ECR repository: {repository_name} (Age: {repo_age})")

def lambda_handler(event, context):
    delete_old_ecr_repositories(event, context)
