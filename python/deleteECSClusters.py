import boto3
from datetime import datetime, timezone, timedelta

def delete_old_ecs_clusters(event, context):
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

        regions = ['ap-southeast-1','ap-southeast-2','us-east-1','us-east-2','us-west-2']

        for region in regions:
            # print(f"Checking region: {region}")
            ecs_region = boto3.client('ecs', region_name=region,
                                      aws_access_key_id=credentials['AccessKeyId'],
                                      aws_secret_access_key=credentials['SecretAccessKey'],
                                      aws_session_token=credentials['SessionToken'])
        
            # Get a list of all ECS clusters in the specified region
            clusters_response = ecs_region.list_clusters()
            cluster_arns = clusters_response['clusterArns']
            
            # Iterate over each cluster and delete it if it's older than 6 hours
            for cluster_arn in cluster_arns:
                cluster_name = cluster_arn.split('/')[-1]
                # Describe the cluster to get its details
                describe_response = ecs_region.describe_clusters(clusters=[cluster_name])
                if describe_response['clusters']:
                    cluster = describe_response['clusters'][0]
                    registered_container_instances_count = cluster.get('registeredContainerInstancesCount', 0)
                    running_tasks_count = cluster.get('runningTasksCount', 0)
                    pending_tasks_count = cluster.get('pendingTasksCount', 0)
                    active_services_count = cluster.get('activeServicesCount', 0)
                    
                    # Check if the cluster is older than 6 hours and all counts are 0
                    if (registered_container_instances_count == 0 and 
                        running_tasks_count == 0 and 
                        pending_tasks_count == 0 and 
                        active_services_count == 0):
                        print(f"Deleting ECS cluster: {cluster_name})")
                        ecs_region.delete_cluster(cluster=cluster_name)
                    else:
                        print(f"Cluster {cluster_name} is not eligible for deletion (Counts: registered={registered_container_instances_count}, running={running_tasks_count}, pending={pending_tasks_count}, active={active_services_count})")

def lambda_handler(event, context):
    delete_old_ecs_clusters(event, context)
