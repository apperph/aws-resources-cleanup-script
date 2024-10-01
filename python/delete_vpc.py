import boto3
import os
from datetime import datetime, timedelta
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

# Function to get creation date from tags
def get_vpc_creation_date(vpc):
    for tag in vpc.get('Tags', []):
        if tag['Key'] == 'CreateDate':  # Assuming VPC has a 'CreateDate' tag
            return tag['Value']
    return None

# Function to retrieve VPC-related resources
def get_vpc_resources(ec2_client, vpc_id):
    subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
    igws = ec2_client.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])['InternetGateways']
    eips = ec2_client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])['Addresses']
    return subnets, igws, eips

# Function to delete VPC and its related resources
def delete_vpc_resources(ec2_client, vpc_id, subnets, igws, eips):
    # Delete Internet Gateways
    for igw in igws:
        igw_id = igw['InternetGatewayId']
        ec2_client.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        ec2_client.delete_internet_gateway(InternetGatewayId=igw_id)
        print(f"Deleted IGW {igw_id} attached to VPC {vpc_id}")

    # Release Elastic IPs
    for eip in eips:
        allocation_id = eip['AllocationId']
        ec2_client.release_address(AllocationId=allocation_id)
        print(f"Released EIP {allocation_id}")

    # Delete Subnets
    for subnet in subnets:
        subnet_id = subnet['SubnetId']
        ec2_client.delete_subnet(SubnetId=subnet_id)
        print(f"Deleted Subnet {subnet_id}")

    # Delete VPC
    ec2_client.delete_vpc(VpcId=vpc_id)
    print(f"Deleted VPC {vpc_id}")

# Main handler
def lambda_handler(event, context):
    threshold_date = datetime.now() - timedelta(days=60)

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
                    creation_date_str = get_vpc_creation_date(vpc)

                    if creation_date_str:
                        vpc_creation_date = datetime.strptime(creation_date_str, '%Y-%m-%d')
                        if vpc_creation_date < threshold_date:
                            print(f"VPC {vpc_id} in account {account_id} in region {region} is older than 2 months. Proceeding with deletion.")
                            
                            subnets, igws, eips = get_vpc_resources(ec2_client, vpc_id)
                            delete_vpc_resources(ec2_client, vpc_id, subnets, igws, eips)
                        else:
                            print(f"VPC {vpc_id} in account {account_id} in region {region} is newer than 2 months.")
                    else:
                        print(f"VPC {vpc_id} does not have a 'CreateDate' tag.")
            except ClientError as e:
                print(f"Error processing VPCs in region {region} for account {account_id}: {e}")

    return {
        'statusCode': 200,
        'body': 'VPC cleanup operation completed'
    }
