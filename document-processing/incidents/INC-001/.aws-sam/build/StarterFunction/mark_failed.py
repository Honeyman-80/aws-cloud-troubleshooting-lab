import json
import os
import time
import boto3

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['JOBS_TABLE']
TOPIC_ARN = os.environ['NOTIFICATION_TOPIC_ARN']

def handler(event, context):
    job_id = event.get('job_id', 'UNKNOWN')
    error = event.get('error', {})

    if job_id != 'UNKNOWN':
        table = dynamodb.Table(TABLE_NAME)
        table.update_item(
            Key={'job_id': job_id},
            UpdateExpression='SET #s = :s, failure_error = :error, failed_at = :now, updated_at = :now',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':s': 'FAILED',
                ':error': json.dumps(error),
                ':now': int(time.time())
            }
        )

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject='Document processing failed',
        Message=json.dumps(event, indent=2)
    )

    return event
