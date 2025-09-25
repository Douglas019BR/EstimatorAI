import json
import boto3
import os
import uuid

sqs = boto3.client('sqs')

SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        requirements = body.get('requirements', '')
        additional_considerations = body.get('additional_considerations', '')
        
        if not requirements:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing requirements parameter'})
            }
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Send to SQS for async processing
        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps({
                'request_id': request_id,
                'requirements': requirements,
                'additional_considerations': additional_considerations
            })
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'request_id': request_id,
                'status': 'processing'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
