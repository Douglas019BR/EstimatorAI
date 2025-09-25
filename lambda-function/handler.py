import json
import boto3
import os
import uuid
from datetime import datetime
import threading

bedrock = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')

with open(os.path.join(os.path.dirname(__file__), 'prompt.md'), 'r') as f:
    PROMPT_TEMPLATE = f.read()

S3_BUCKET = os.environ.get('S3_BUCKET', 'estimator-ai-results')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        requirements = body.get('requirements', '')
        
        if not requirements:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing requirements parameter'})
            }
        
        request_id = str(uuid.uuid4())
        
        # Start async processing
        thread = threading.Thread(
            target=process_estimation_async,
            args=(request_id, requirements)
        )
        thread.start()
        
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

def process_estimation_async(request_id, requirements):
    try:
        estimation = generate_project_estimation(requirements)
        save_result_to_s3(request_id, requirements, estimation)
    except Exception as e:
        save_error_to_s3(request_id, str(e))

def generate_project_estimation(requirements):
    prompt = PROMPT_TEMPLATE.format(requirements=requirements)

    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 4000,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    
    result = json.loads(response['body'].read())
    content = result['content'][0]['text']
    
    try:
        return json.loads(content)
    except Exception as e:
        return {
            'refined_requirements': content,
            'tasks': [],
            'work_plan': content,
            'total_estimated_hours': 0,
            'error': f'Failed to parse JSON: {str(e)}'
        }

def save_result_to_s3(request_id, requirements, estimation):
    data = {
        'request_id': request_id,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'input_requirements': requirements,
        'result': estimation
    }
    
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f'results/{request_id}.json',
        Body=json.dumps(data),
        ContentType='application/json'
    )

def save_error_to_s3(request_id, error):
    data = {
        'request_id': request_id,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'error',
        'error': error
    }
    
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f'results/{request_id}.json',
        Body=json.dumps(data),
        ContentType='application/json'
    )
