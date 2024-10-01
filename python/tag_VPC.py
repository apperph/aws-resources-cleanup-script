import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

# Environment variables for role and regions
aws_regions = ['ap-southeast-1','ap-southeast-2','us-east-1','us-east-2','us-west-2']
account_ids = ['707125572044', '058690268851', '584782747967', '236921907600', '562032292525']

# Helper function to assume a role in the target account
def assume_role(account_id):
    sts_client = boto3.client('sts')
    try:
        response = sts_client.assume_role(
            RoleArn=f'arn:aws:iam::{account_id}:role/LambdaCostOptimization',
            RoleSessionName='AssumedRoleSession'
        )
        return response['Credentials']
    except ClientError as e:
        print(f"Error assuming role for account {account_id}: {e}")
        return None

# Function to tag VPCs with 'CreateDate'
def tag_vpcs_with_creation_date(ec2_client, vpc_id):
    try:
        # Get current date in 'YYYY-MM-DD' format
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Add/Create the 'CreateDate' tag
        ec2_client.create_tags(
            Resources=[vpc_id],
            Tags=[
                {'Key': 'CreateDate', 'Value': current_date}
            ]
        )
        print(f"Tagged VPC {vpc_id} with CreateDate: {current_date}")
    except ClientError as e:
        print(f"Error tagging VPC {vpc_id}: {e}")

# Main handler
def lambda_handler(event, context):
    for account_id in account_ids:
        creds = assume_role(account_id)
        if creds is None:
            continue  # Skip to the next account if assume role fails

        for region in aws_regions:
            ec2_client = boto3.client(
                'ec2',
                region_name=region,
                aws_access_key_id=creds['AccessKeyId'],
                aws_secret_access_key=creds['SecretAccessKey'],
                aws_session_token=creds['SessionToken']
            )

            try:
                # Describe VPCs in the region
                vpcs = ec2_client.describe_vpcs()['Vpcs']
                for vpc in vpcs:
                    vpc_id = vpc['VpcId']
                    existing_tags = {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}

                    # Check if the VPC already has a 'CreateDate' tag
                    if 'CreateDate' not in existing_tags:
                        # Tag the VPC with the current date as 'CreateDate'
                        tag_vpcs_with_creation_date(ec2_client, vpc_id)
                    else:
                        print(f"VPC {vpc_id} in account {account_id} in region {region} already has a CreateDate tag: {existing_tags['CreateDate']}")
            except ClientError as e:
                print(f"Error processing VPCs in region {region} for account {account_id} in region {region}: {e}")

    return {
        'statusCode': 200,
        'body': 'VPC tagging operation completed'
    }
