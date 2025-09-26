import json
import boto3
import os
import uuid
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')

SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

def lambda_handler(event, context):
    # Log incoming event
    logger.info(f"Received event: {json.dumps(event, default=str)}")
    
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        requirements = body.get('requirements', '')
        additional_considerations = body.get('additional_considerations', '')
        
        logger.info(f"Parsed body - requirements: {requirements[:100]}..., additional_considerations: {additional_considerations}")
        
        if not requirements:
            response = {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Missing requirements parameter'})
            }
            logger.info(f"Sending error response: {json.dumps(response)}")
            return response
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        logger.info(f"Generated request_id: {request_id}")
        
        # Send to SQS for async processing
        sqs_message = {
            'request_id': request_id,
            'requirements': requirements,
            'additional_considerations': additional_considerations
        }
        
        logger.info(f"Sending to SQS: {json.dumps(sqs_message)}")
        
        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(sqs_message)
        )
        
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'request_id': request_id,
                'status': 'processing'
            })
        }
        
        logger.info(f"Sending success response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}", exc_info=True)
        response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }
        logger.info(f"Sending error response: {json.dumps(response)}")
        return response
