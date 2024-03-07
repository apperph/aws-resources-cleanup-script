#!/bin/bash

# Set the AWS region and AWS Profile to use
AWS_REGION="your-region"
PROFILE="<sso-profile>"

# Get list of RDS snapshots
SNAPSHOTS=$(aws rds describe-db-snapshots --region $AWS_REGION --query "DBSnapshots[].DBSnapshotIdentifier" --output text --profile "$PROFILE")

# Loop through each snapshot and delete it
for SNAPSHOT_ID in $SNAPSHOTS
do
    echo "Deleting RDS snapshot: $SNAPSHOT_ID"
    aws rds delete-db-snapshot --region $AWS_REGION --db-snapshot-identifier "$SNAPSHOT_ID" --profile "$PROFILE"
done
