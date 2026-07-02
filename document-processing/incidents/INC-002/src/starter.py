import json
import os
import urllib.parse
import boto3

sfn = boto3.client('stepfunctions')
STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']

def handler(event, context):
    for record in event.get('Records', []):
        body = json.loads(record['body'])
        for s3_record in body.get('Records', []):
            bucket = s3_record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(s3_record['s3']['object']['key'])
            parts = key.split('/')
            job_id = parts[1] if len(parts) >= 3 and parts[0] == 'uploads' else key

            workflow_input = {
                'job_id': job_id,
                's3_bucket': bucket,
                's3_key': key
            }

            sfn.start_execution(
                stateMachineArn=STATE_MACHINE_ARN,
                input=json.dumps(workflow_input)
            )

    return {'started': True}
