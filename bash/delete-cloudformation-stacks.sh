#!/bin/bash

region="ap-southeast-1"

PROFILE="<sso-profile>" # Change this to your sso profile

# Get all CloudFormation stack names and IDs in the Singapore region
stacks=$(aws cloudformation list-stacks --region $region --profile "$PROFILE" --query "StackSummaries[?StackStatus != 'DELETE_COMPLETE'][].{Name: StackName, ID: StackId}" | grep -v "StackSet")

# Loop through the stacks and delete them
for stack in $(echo "$stacks" | jq -r '.[] | @base64'); do
    name=$(echo "$stack" | base64 --decode | jq -r '.Name')
    id=$(echo "$stack" | base64 --decode | jq -r '.ID')
    # Delete the stack
    aws cloudformation delete-stack --region $region --stack-name $name --profile "$PROFILE"
    echo "Stack $name ($id) deleted successfully."
done