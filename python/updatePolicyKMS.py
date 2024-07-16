import boto3
import json

def update_kms_key_policy(event, context):
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

            # List all KMS keys
            paginator = kms_client.get_paginator('list_keys')
            for page in paginator.paginate():
                for key in page['Keys']:
                    key_id = key['KeyId']

                # Retrieve the current key policy
                policy = kms_client.get_key_policy(KeyId=key_id, PolicyName='default')['Policy']
                policy_document = json.loads(policy)
                
                # Define the statement to allow schedule deletion
                schedule_deletion_statement = {
                            "Sid": "AllowPutKeyPolicy",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "kms:PutKeyPolicy",
                            "Resource": "*"
                        }
                
                # Check if the statement already exists
                statements = policy_document.get("Statement", [])

                if not any(stmt for stmt in statements if stmt.get("Sid") == "AllowPutKeyPolicy"):
                    statements.append(schedule_deletion_statement)
                    policy_document["Statement"] = statements
                    
                    # Update the key policy
                    kms_client.put_key_policy(
                        KeyId=key_id,
                        PolicyName='default',
                        Policy=json.dumps(policy_document)
                    )
                    print(f"Updated policy for key: {key_id}")
                else:
                    print(f"Policy already updated for key: {key_id}")

def lambda_handler(event, context):
    update_kms_key_policy(event, context)

