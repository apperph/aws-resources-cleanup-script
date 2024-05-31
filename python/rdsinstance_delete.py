import boto3
from datetime import datetime, timedelta, timezone
import os

def stop_rds_instances(event, context):
    # Define a list of AWS account IDs to check
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

        # Get a list of all regions
        rds = boto3.client('rds', aws_access_key_id=credentials['AccessKeyId'],
                           aws_secret_access_key=credentials['SecretAccessKey'],
                           aws_session_token=credentials['SessionToken'])
        regions = ['ap-southeast-1','ap-southeast-2','us-east-1','us-east-2','us-west-2']
        
        # Get the current time
        now = datetime.now(timezone.utc)
        
        # Get all running RDS instances in the current account
                # Iterate over all regions
        for region in regions:
            # print(f"Checking region: {region}")
            rds_region = boto3.client('rds', region_name=region,
                                      aws_access_key_id=credentials['AccessKeyId'],
                                      aws_secret_access_key=credentials['SecretAccessKey'],
                                      aws_session_token=credentials['SessionToken'])
            dbinstances = rds_region.describe_db_instances()
            count=len(dbinstances['DBInstances'])
            print(f"{count} instances are found running in {region} of account {account_id}")

            # Iterate through each databases to check instance launch time            
            for database in dbinstances['DBInstances']:
                for instance_id in database['DBInstanceIdentifier']:
                    launch_time = database['InstanceCreateTime']
                    
                    # Calculate the time difference between current time and launch time
                    running_time = now - launch_time
                    # If running time is more than 5 hours, stop the instance
                    if running_time > timedelta(hours=4):
                        rds_region.delete_db_instance(
                DBInstanceIdentifier=database['DBInstanceIdentifier'],
                SkipFinalSnapshot=True
            )
                        print(f"Instance {instance_id} from account {account_id} stopped as it was running for more than 4 hours.")
                    else:
                        print(f"Instance {instance_id} from account {account_id} is running for less than 4 hours.")

# Entry point of the Lambda function
def lambda_handler(event, context):
    stop_rds_instances(event, context)
