#!/bin/bash

# Set the AWS region where the ElastiCache clusters exist
AWS_REGION="your-aws-region"

# Get a list of all ElastiCache cluster identifiers in the specified region
clusters=$(aws elasticache describe-cache-clusters --region $AWS_REGION --query 'CacheClusters[*].CacheClusterId' --output text)

# Check if any clusters exist
if [ -z "$clusters" ]; then
    echo "No ElastiCache clusters found in the specified region."
    exit 0
fi

# Delete each ElastiCache cluster
for cluster in $clusters; do
    echo "Deleting ElastiCache cluster: $cluster"
    aws elasticache delete-cache-cluster --region $AWS_REGION --cache-cluster-id $cluster --final-snapshot-identifier "$cluster-final-snapshot"
done
