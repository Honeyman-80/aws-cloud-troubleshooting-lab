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

    obj = s3.get_object(Bucket=bucket, Key=key)
    content = obj['Body'].read(2048)

    extracted = {
        'preview_bytes': len(content),
        'detected_type': obj.get('ContentType', 'unknown')
    }

    table = dynamodb.Table(TABLE_NAME)
    table.update_item(
        Key={'job_id': job_id},
        UpdateExpression='SET #s = :s, extracted = :extracted, updated_at = :now',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':s': 'EXTRACTED',
            ':extracted': extracted,
            ':now': int(time.time())
        }
    )

    event['extracted'] = extracted
    return event
