import os
import time
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['JOBS_TABLE']

def handler(event, context):
    job_id = event['job_id']
    bucket = event['s3_bucket']
    key = event['s3_key']

    head = s3.head_object(Bucket=bucket, Key=key)
    size = head.get('ContentLength', 0)

    if size <= 0:
        raise ValueError('Uploaded object is empty')

    table = dynamodb.Table(TABLE_NAME)
    table.update_item(
        Key={'job_id': job_id},
        UpdateExpression='SET #s = :s, object_size = :size, updated_at = :now',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':s': 'VALIDATED',
            ':size': size,
            ':now': int(time.time())
        }
    )

    event['object_size'] = size
    return event
