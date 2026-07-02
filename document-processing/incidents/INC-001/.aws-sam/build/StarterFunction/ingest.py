import json
import os
import time
import uuid
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ['JOBS_TABLE']
BUCKET = os.environ['UPLOAD_BUCKET']
EXPIRY_SECONDS = int(os.environ.get('URL_EXPIRY_SECONDS', '900'))

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }

def handler(event, context):
    body = json.loads(event.get('body') or '{}')
    filename = body.get('filename')
    content_type = body.get('content_type', 'application/octet-stream')

    if not filename:
        return response(400, {'message': 'filename is required'})

    job_id = str(uuid.uuid4())
    s3_key = f'uploads/{job_id}/{filename}'
    now = int(time.time())

    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item={
        'job_id': job_id,
        'filename': filename,
        'content_type': content_type,
        's3_bucket': BUCKET,
        's3_key': s3_key,
        'status': 'AWAITING_UPLOAD',
        'created_at': now,
        'updated_at': now
    })

    upload_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': BUCKET,
            'Key': s3_key,
            'ContentType': content_type
        },
        ExpiresIn=EXPIRY_SECONDS
    )

    return response(202, {
        'job_id': job_id,
        'upload_url': upload_url,
        's3_bucket': BUCKET,
        's3_key': s3_key,
        'expires_in_seconds': EXPIRY_SECONDS
    })
