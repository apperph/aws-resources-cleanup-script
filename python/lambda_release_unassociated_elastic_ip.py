import boto3

def release_unassociated_eip(event, context):
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
        ec2 = boto3.client('ec2', aws_access_key_id=credentials['AccessKeyId'],
                           aws_secret_access_key=credentials['SecretAccessKey'],
                           aws_session_token=credentials['SessionToken'])
        regions = ['ap-southeast-1','ap-southeast-2','us-east-1','us-east-2','us-west-2']

        # Iterate over all regions
        for region in regions:
            print(f"Checking region: {region}")
            ec2_region = boto3.client('ec2', region_name=region,
                                      aws_access_key_id=credentials['AccessKeyId'],
                                      aws_secret_access_key=credentials['SecretAccessKey'],
                                      aws_session_token=credentials['SessionToken'])

            # Get list of unassociated Elastic IPs
            response = ec2_region.describe_addresses()
            unassociated_ips = [addr['AllocationId'] for addr in response['Addresses'] if 'AssociationId' not in addr]

            # Loop through each unassociated Elastic IP and delete it
            for allocation_id in unassociated_ips:
                print(f"Deleting unassociated Elastic IP: {allocation_id} in region {region}")
                ec2_region.release_address(AllocationId=allocation_id)

    # Return a success response only if there were unassociated Elastic IPs to delete
        if unassociated_ips:
            print(f"Deleted unassociated Elastic IPs on account {account_id} successfully")
        else:
            print(f"No unassociated Elastic IPs on account {account_id} to delete")

# Entry point of the Lambda function
def lambda_handler(event, context):
    release_unassociated_eip(event, context)