#!/bin/bash

REGION="ap-southeast-1"  # Change this to your desired region

PROFILE="AWSAdministratorAccess-584782747967"  # Change this to your sso profile

# Get the instance IDs of all running instances in the specified region
INSTANCE_IDS=$(aws ec2 describe-instances --region "$REGION" --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].InstanceId" --output text --profile "$PROFILE")

if [[ -z $INSTANCE_IDS ]]; then
  echo "No running instances found in region $REGION."
else
  # Stop the instances
  aws ec2 stop-instances --region "$REGION" --instance-ids $INSTANCE_IDS --profile "$PROFILE"

  # Wait for instances to stop
  echo "Stopping instances..."
  aws ec2 wait instance-stopped --region "$REGION" --instance-ids $INSTANCE_IDS --profile "$PROFILE"

  echo "All running instances in region $REGION have been stopped."
fi
