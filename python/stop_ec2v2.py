import boto3
from datetime import datetime, timedelta, timezone
import os

def stop_old_ec2_instances(event, context):
    # Define a list of AWS account IDs to check
    account_ids = ['707125572044', '058690268851', '584782747967', '236921907600']  # Add more account IDs as needed
    
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
        ec2 = boto3.client('ec2', aws_access_key_id=credentials['AccessKeyId'],
                           aws_secret_access_key=credentials['SecretAccessKey'],
                           aws_session_token=credentials['SessionToken'])
        regions = ['ap-southeast-1','ap-southeast-2','us-east-1','us-east-2','us-west-2']
        
        # Get the current time
        now = datetime.now(timezone.utc)
        
        # Get all running EC2 instances in the current account
                # Iterate over all regions
        for region in regions:
            # print(f"Checking region: {region}")
            ec2_region = boto3.client('ec2', region_name=region,
                                      aws_access_key_id=credentials['AccessKeyId'],
                                      aws_secret_access_key=credentials['SecretAccessKey'],
                                      aws_session_token=credentials['SessionToken'])
            instances = ec2_region.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
            count=len(instances['Reservations'])
            print(f"{count} instances are found running in {region} of account {account_id}")

            # Iterate through each reservation to check instance launch time            
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    launch_time = instance['LaunchTime']
                    
                    # Calculate the time difference between current time and launch time
                    running_time = now - launch_time
                    # If running time is more than 5 hours, stop the instance
                    if running_time > timedelta(hours=5):
                        ec2_region.stop_instances(InstanceIds=[instance_id])
                        print(f"Instance {instance_id} from account {account_id} stopped as it was running for more than 5 hours.")
                    else:
                        print(f"Instance {instance_id} from account {account_id} is running for less than 5 hours.")

# Entry point of the Lambda function
def lambda_handler(event, context):
    stop_old_ec2_instances(event, context)
