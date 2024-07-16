import boto3
from datetime import datetime, timezone, timedelta

def delete_old_services_and_tasks(event, context):
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
            ecs_client = boto3.client('ecs', region_name=region,
                                      aws_access_key_id=credentials['AccessKeyId'],
                                      aws_secret_access_key=credentials['SecretAccessKey'],
                                      aws_session_token=credentials['SessionToken'])
    
            # Get a list of all ECS clusters in the specified region
            clusters_response = ecs_client.list_clusters()
            cluster_arns = clusters_response['clusterArns']
            
            # Iterate over each cluster and delete it if it's older than 6 hours
            for cluster_arn in cluster_arns:
                cluster_name = cluster_arn.split('/')[-1]
                
                # Get the list of services in the cluster
                services_response = ecs_client.list_services(cluster=cluster_name)
                service_arns = services_response['serviceArns']
                
                # Describe the services to get their details
                services = ecs_client.describe_services(cluster=cluster_name, services=service_arns)['services']
                
                # Iterate over each service and delete it if it's older than 6 hours
                for service in services:
                    created_at = service.get('createdAt')
                    if created_at:
                        service_age = datetime.now(timezone.utc) - created_at
                        if service_age > timedelta(hours=6):
                            service_name = service['serviceName']
                            print(f"Deleting ECS service: {service_name} (Age: {service_age})")
                            ecs_client.update_service(cluster=cluster_name, service=service_name, desiredCount=0)
                            ecs_client.delete_service(cluster=cluster_name, service=service_name)
                        else:
                            print(f"Skipping ECS service: {service['serviceName']} (Age: {service_age})")

                # Get the list of tasks in the cluster
                tasks_response = ecs_client.list_tasks(cluster=cluster_name)
                task_arns = tasks_response['taskArns']
                
                # Describe the tasks to get their details
                tasks = ecs_client.describe_tasks(cluster=cluster_name, tasks=task_arns)['tasks']
                
                # Iterate over each task and stop it if it's older than 6 hours
                for task in tasks:
                    task_started_at = task.get('startedAt')
                    if task_started_at:
                        task_age = datetime.now(timezone.utc) - task_started_at
                        if task_age > timedelta(hours=6):
                            task_arn = task['taskArn']
                            print(f"Stopping ECS task: {task_arn} (Age: {task_age})")
                            ecs_client.stop_task(cluster=cluster_name, task=task_arn)
                        else:
                            print(f"Skipping ECS task: {task['taskArn']} (Age: {task_age})")

def lambda_handler(event, context):
    delete_old_services_and_tasks(event, context)
