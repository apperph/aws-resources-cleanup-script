import boto3
from datetime import datetime, timedelta, timezone
import os

def delete_old_nat_gateways(event, context):
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
            print(f"Checking region {region} of account {account_id}")
            ec2_region = boto3.client('ec2', region_name=region,
                                      aws_access_key_id=credentials['AccessKeyId'],
                                      aws_secret_access_key=credentials['SecretAccessKey'],
                                      aws_session_token=credentials['SessionToken'])
            nat_gateways = ec2_region.describe_nat_gateways()
            count=len(nat_gateways['NatGateways'])
            print(f"{count} NAT Gateways are found in {region} of account {account_id}")


            # Iterate through each NAT gateway to check NAT gateway creation time          
            for nat_gateway in nat_gateways['NatGateways']:
                nat_gateway_id = nat_gateway['NatGatewayId']
                create_time = nat_gateway['CreateTime']
                    
                # Calculate the time difference between current time and launch time
                running_time = now - create_time

                # Check if the NAT gateway is older than 12 hours
                if running_time > timedelta(hours=12):
                    print(f"NAT Gateway {nat_gateway_id} of account {account_id} is older than 12 hours, deleting...")
                    # Delete the NAT gateway
                    ec2_region.delete_nat_gateway(NatGatewayId=nat_gateway_id)
                    print(f"Deleted NAT Gateway {nat_gateway_id}")
                else:
                    print(f"NAT Gateway {nat_gateway_id} of account {account_id} is created less than 12 hours ago.")

# Entry point of the Lambda function
def lambda_handler(event, context):
    delete_old_nat_gateways(event, context)
