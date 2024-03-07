#!/bin/bash

# Set the AWS region and AWS Profile to use
AWS_REGION="your-region"
PROFILE="<sso-profile>"

# Get list of unassociated Elastic IPs
UNASSOCIATED_IPS=$(aws ec2 describe-addresses --region $AWS_REGION --query "Addresses[?AssociationId == null].AllocationId" --output text --profile "$PROFILE")

# Loop through each unassociated Elastic IP and delete it
for ALLOCATION_ID in $UNASSOCIATED_IPS
do
    echo "Deleting unassociated Elastic IP: $ALLOCATION_ID"
    aws ec2 release-address --region $AWS_REGION --allocation-id $ALLOCATION_ID --profile "$PROFILE"
done
