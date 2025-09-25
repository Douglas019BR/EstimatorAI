import json
import boto3
import os
from datetime import datetime

bedrock = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')

with open(os.path.join(os.path.dirname(__file__), 'prompt.md'), 'r') as f:
    PROMPT_TEMPLATE = f.read()

S3_BUCKET = os.environ.get('S3_BUCKET', 'estimator-ai-results')

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            message = json.loads(record['body'])
            request_id = message['request_id']
            requirements = message['requirements']
            additional_considerations = message.get('additional_considerations', '')
            
            # Process estimation
            estimation = generate_project_estimation(requirements, additional_considerations)
            
            # Save to S3
            save_result_to_s3(request_id, requirements, additional_considerations, estimation)
                
    except Exception as e:
        print(f"Error processing request: {e}")
        # Save error to S3
        if 'request_id' in locals():
            save_error_to_s3(request_id, str(e))
        raise

def generate_project_estimation(requirements, additional_considerations):
    prompt = PROMPT_TEMPLATE.format(
        requirements=requirements,
        additional_considerations=additional_considerations
    )

    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
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
    except:
        return {
            'refined_requirements': content,
            'tasks': [],
            'work_plan': content,
            'total_estimated_hours': 0
        }

def save_result_to_s3(request_id, requirements, additional_considerations, estimation):
    data = {
        'request_id': request_id,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'input_requirements': requirements,
        'additional_considerations': additional_considerations,
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
