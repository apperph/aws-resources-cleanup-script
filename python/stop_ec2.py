import boto3
from datetime import datetime, timedelta, timezone
import os

def stop_old_ec2_instances(event, context):
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
        
        # Create an EC2 client using the assumed role's credentials
        ec2 = boto3.client(
            'ec2',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        # Get the current time
        now = datetime.now(timezone.utc)
        
        # Get all running EC2 instances in the current account
        instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        
        # Iterate through each reservation to check instance launch time
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                launch_time = instance['LaunchTime']
                
                # Calculate the time difference between current time and launch time
                running_time = now - launch_time
                
                # If running time is more than 5 hours, stop the instance
                if running_time > timedelta(hours=5):
                    ec2.stop_instances(InstanceIds=[instance_id])
                    print(f"Instance {instance_id} from account {account_id} stopped as it was running for more than 5 hours.")
                else:
                    print(f"Instance {instance_id} from account {account_id} is running for less than 5 hours.")

# Entry point of the Lambda function
def lambda_handler(event, context):
    stop_old_ec2_instances(event, context)
