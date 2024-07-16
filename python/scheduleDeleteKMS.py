import boto3

def schedule_kms_key_deletion(event, context):
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
            # Create a KMS client
            kms_client = boto3.client('kms', region_name=region,
                                            aws_access_key_id=credentials['AccessKeyId'],
                                            aws_secret_access_key=credentials['SecretAccessKey'],
                                            aws_session_token=credentials['SessionToken'])
            
            keys = []
            paginator = kms_client.get_paginator('list_keys')
            for page in paginator.paginate():
                keys.extend(page['Keys'])
            
            # Schedule deletion for each KMS key
            for key in keys:
                key_id = key['KeyId']
                # Schedule the deletion of the KMS key
                response = kms_client.schedule_key_deletion(
                    KeyId=key_id,
                    PendingWindowInDays=7  # Schedule deletion in 7 days
                )
                print(f"Scheduled deletion of KMS key {key_id} in 7 days.")

def lambda_handler(event, context):
    schedule_kms_key_deletion(event, context)
