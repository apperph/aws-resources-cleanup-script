import boto3
import os
from datetime import datetime, timezone, timedelta

def delete_asg(event, context):
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

        temp_session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        aws_regions = ['ap-southeast-1','ap-southeast-2','us-east-1','us-east-2','us-west-2']  # Replace with your list of AWS regions

        for region in aws_regions:
            asg_client = temp_session.client('autoscaling', region_name=region)
            ec2_client = temp_session.client('ec2', region_name=region)

            response = asg_client.describe_auto_scaling_groups()
            for asg in response['AutoScalingGroups']:
                asg_name = asg['AutoScalingGroupName']
                creation_time = asg['CreatedTime']
                age = datetime.now(timezone.utc) - creation_time
                
                if age > timedelta(hours=6):
                    # Set desired capacity to 0
                    asg_client.update_auto_scaling_group(
                        AutoScalingGroupName=asg_name,
                        MinSize=0,
                        DesiredCapacity=0
                    )
                    print(f"Desired count for ASG {asg_name} in {region} for account {account_id} has been set to 0.")

                    # Check if the desired capacity is 0
                    asg_updated = asg_client.describe_auto_scaling_groups(
                        AutoScalingGroupNames=[asg_name]
                    )
                    if asg_updated['AutoScalingGroups'][0]['DesiredCapacity'] == 0:
                        # Terminate the auto scaling group
                        asg_client.delete_auto_scaling_group(
                            AutoScalingGroupName=asg_name,
                            ForceDelete=True
                        )
                        print(f"Terminated ASG {asg_name} in {region} for account {account_id}")
                    
                else:
                    print(f"ASG {asg_name} in {region} for account {account_id} is created less than 6 hours ago.")

# Example event and context for local testing
def lambda_handler(event, context):
    delete_asg(event, context)
