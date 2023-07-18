#!/bin/bash

# Set the AWS region where the EC2 instances exist
AWS_REGION="ap-southeast-1"

PROFILE="<sso-profile>" # Change this to your sso profile

# Get a list of all EC2 instance IDs in the specified region
instances=$(aws ec2 describe-instances --region $AWS_REGION --query 'Reservations[*].Instances[*].InstanceId' --output text --profile "$PROFILE")

# Check if any instances exist
if [ -z "$instances" ]; then
    echo "No EC2 instances found in the specified region."
    exit 0
fi

# Terminate each EC2 instance
for instance in $instances; do
    echo "Terminating EC2 instance: $instance"
    aws ec2 terminate-instances --region $AWS_REGION --instance-ids $instance --profile "$PROFILE"
done
