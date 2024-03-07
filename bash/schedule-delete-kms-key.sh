#!/bin/bash

# Set the AWS region and AWS Profile to use
AWS_REGION="your-region"
PROFILE="<sso-profile>"

# Get list of all CMKs in the specified region
KEYS=$(aws kms list-keys --region $AWS_REGION --query 'Keys[].KeyId' --output text --profile "$PROFILE")

# Set the number of days after which the keys should be deleted
SCHEDULED_DELETION_DAYS="7"

# Loop through each CMK and schedule deletion
for KEY_ID in $KEYS
do
    # Generate a key policy JSON with a deletion schedule
    KEY_POLICY=$(cat <<EOF
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow Scheduled Key Deletion",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "kms:ScheduleKeyDeletion",
      "Resource": "*",
      "Condition": {
        "DateLessThan": {
          "kms:DeletionDate": {
            "AWS:EpochTime": $(($(date +%s) + $SCHEDULED_DELETION_DAYS * 24 * 3600))
          }
        }
      }
    }
EOF
)

    # Update the key policy to schedule deletion
    aws kms put-key-policy --region $AWS_REGION --key-id $KEY_ID --policy-name default --policy "$KEY_POLICY" --profile "$PROFILE"
    echo "Scheduled deletion for CMK: $KEY_ID"
done
