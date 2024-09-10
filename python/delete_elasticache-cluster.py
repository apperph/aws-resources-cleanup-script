import boto3
from datetime import datetime, timezone, timedelta
import os

def delete_elasticachecluster(event, context):
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
        min_age_hours = 6  # Minimum age in hours before deleting a cluster
        now = datetime.now(timezone.utc)

        for region in aws_regions:
            print(f"Processing region: {region}")
            elasticache = temp_session.client('elasticache', region_name=region)

            response = elasticache.describe_cache_clusters()
            clusters = [cluster for cluster in response['CacheClusters']]

            if not clusters:
                print(f"No ElastiCache clusters found in region: {region}")
                continue

            for cluster in clusters:
                creation_time = cluster['CacheClusterCreateTime']
                age_in_timedelta = (now - creation_time)
                age_in_hours = age_in_timedelta.total_seconds() / 3600

                if age_in_hours > min_age_hours:
                    print(f"Deleting ElastiCache cluster: {cluster['CacheClusterId']} in region: {region}")
                    if 'ReplicationGroupId' in cluster:
                        elasticache.delete_replication_group(
                            ReplicationGroupId=cluster['ReplicationGroupId']
                        )
                    else:
                        elasticache.delete_cache_cluster(
                            CacheClusterId=cluster['CacheClusterId']
                        )
                else:
                    print(f"Skipping ElastiCache cluster: {cluster['CacheClusterId']} in region: {region} because it is less than {min_age_hours} hours old.")

    return {
        'statusCode': 200,
        'statusMessage': 'ElastiCache clusters deleted successfully across all regions'
    }


def lambda_handler(event, context):
    delete_elasticachecluster(event, context)