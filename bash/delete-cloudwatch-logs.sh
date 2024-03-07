#!/bin/bash

# Set the AWS region and AWS Profile to use
AWS_REGION="your-region"
PROFILE="<sso-profile>"

# Get list of CloudWatch Log groups
LOG_GROUPS=$(aws logs describe-log-groups --region $AWS_REGION --query "logGroups[].logGroupName" --output text --profile "$PROFILE")

# Loop through each log group and delete it
for LOG_GROUP in $LOG_GROUPS
do
    echo "Deleting CloudWatch Log group: $LOG_GROUP"
    aws logs delete-log-group --region $AWS_REGION --log-group-name "$LOG_GROUP" --profile "$PROFILE"
done
