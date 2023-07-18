#!/bin/bash

# Set the AWS region where the EC2 instances exist
AWS_REGION="ap-southeast-1"

PROFILE="<sso-profile>" # Change this to your sso profile

# Fetch list of EBS volumes
volumes=$(aws ec2 describe-volumes --region $AWS_REGION --query "Volumes[?State=='available'].VolumeId" --output text --profile "$PROFILE")

# Check if any volumes exist
if [ -z "$volumes" ]; then
    echo "No unattached EBS Volumes found in the specified region."
    exit 0
fi

# Delete each volume
for volume in $volumes; do
    echo "Deleting volume: $volume"
    aws ec2 delete-volume --region $AWS_REGION --volume-id $volume --profile "$PROFILE"
done
