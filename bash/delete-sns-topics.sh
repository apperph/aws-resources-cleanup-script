#!/bin/bash

# Set the AWS region and AWS Profile to use
AWS_REGION="your-region"
PROFILE="<sso-profile>"

# Get list of SNS topics
TOPICS=$(aws sns list-topics --query 'Topics[].TopicArn' --region $AWS_REGION --output text --profile "$PROFILE")

# Loop through each topic and delete it
for TOPIC_ARN in $TOPICS
do
    echo "Deleting SNS topic: $TOPIC_ARN"
    aws sns delete-topic --topic-arn "$TOPIC_ARN" --region $AWS_REGION --profile "$PROFILE"
done
