import boto3
from datetime import datetime, timezone, timedelta

def terminate_stopped_instances_in_accounts(event, context):
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
            response = ec2_region.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
            
            # Loop through the stopped EC2 instances
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    launch_time = instance['LaunchTime']
                    
                    running_time = now - launch_time
                    # If stopped for more than 1 day, delete the instance
                    if running_time > timedelta(days=1):
                        ec2_region.stop_instances(InstanceIds=[instance_id])
                        print(f"Instance {instance_id} from account {account_id} terminated")
                    else:
                        print(f"Instance {instance_id} from account {account_id} is stopped for less than 1 day.")

def lambda_handler(event, context):
    terminate_stopped_instances_in_accounts(event, context)
