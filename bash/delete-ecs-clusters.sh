#!/bin/bash

# Set the AWS region where the ECS clusters exist
AWS_REGION="your-aws-region"

# Get a list of all ECS clusters in the specified region
clusters=$(aws ecs list-clusters --region $AWS_REGION --output text | awk '{print $2}')

# Iterate over each cluster and delete it
for cluster in $clusters; do
    echo "Deleting ECS cluster: $cluster"
    aws ecs delete-cluster --cluster $cluster --region $AWS_REGION
done
