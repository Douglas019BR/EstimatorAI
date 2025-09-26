import json
import boto3
import os
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
s3 = boto3.client('s3')

with open(os.path.join(os.path.dirname(__file__), 'prompt.md'), 'r') as f:
    PROMPT_TEMPLATE = f.read()

S3_BUCKET = os.environ.get('S3_BUCKET', 'estimator-ai-results')
MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event, default=str)}")
    
    try:
        for record in event['Records']:
            logger.info(f"Processing record: {json.dumps(record, default=str)}")
            
            message = json.loads(record['body'])
            request_id = message['request_id']
            requirements = message['requirements']
            additional_considerations = message.get('additional_considerations', '')
            
            logger.info(f"Processing request_id: {request_id}")
            logger.info(f"Requirements: {requirements[:200]}...")
            logger.info(f"Additional considerations: {additional_considerations}")
            
            # Process estimation
            logger.info("Starting estimation generation...")
            estimation = generate_project_estimation(requirements, additional_considerations)
            logger.info(f"Estimation generated successfully: {json.dumps(estimation, default=str)[:500]}...")
            
            # Save to S3
            logger.info(f"Saving result to S3 bucket: {S3_BUCKET}")
            save_result_to_s3(request_id, requirements, additional_considerations, estimation)
            logger.info(f"Result saved successfully for request_id: {request_id}")
                
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        # Save error to S3
        if 'request_id' in locals():
            logger.info(f"Saving error to S3 for request_id: {request_id}")
            save_error_to_s3(request_id, str(e))
        raise

def generate_project_estimation(requirements, additional_considerations):
    logger.info("Preparing prompt for Bedrock...")
    
    try:
        prompt = PROMPT_TEMPLATE.format(
            requirements=requirements,
            additional_considerations=additional_considerations
        )
        logger.info(f"Prompt prepared successfully, length: {len(prompt)} characters")
        logger.info(f"Full prompt being sent to Bedrock:\n{prompt}")
        
    except KeyError as e:
        logger.error(f"KeyError in prompt formatting: {str(e)}")
        logger.error(f"Available template keys: requirements, additional_considerations")
        logger.error(f"Provided requirements: {requirements}")
        logger.error(f"Provided additional_considerations: {additional_considerations}")
        raise

    logger.info("Invoking Bedrock model...")
    bedrock_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }
    logger.info(f"Bedrock request payload: {json.dumps(bedrock_request, default=str)}")
    
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(bedrock_request)
    )
    
    result = json.loads(response['body'].read())
    content = result['content'][0]['text']
    logger.info(f"Bedrock response received, content length: {len(content)} characters")
    logger.info(f"Full Bedrock response:\n{content}")
    
    try:
        parsed_result = json.loads(content)
        logger.info("Successfully parsed JSON response from Bedrock")
        logger.info(f"Parsed result keys: {list(parsed_result.keys())}")
        return parsed_result
    except Exception as parse_error:
        logger.warning(f"Failed to parse JSON response: {str(parse_error)}")
        logger.warning(f"Raw content that failed to parse:\n{content}")
        logger.info("Returning fallback structure")
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
    
    logger.info(f"Saving to S3 - Bucket: {S3_BUCKET}, Key: results/{request_id}.json")
    
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f'results/{request_id}.json',
        Body=json.dumps(data, default=str),
        ContentType='application/json'
    )
    
    logger.info(f"Successfully saved result to S3 for request_id: {request_id}")

def save_error_to_s3(request_id, error):
    data = {
        'request_id': request_id,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'error',
        'error': error
    }
    
    logger.info(f"Saving error to S3 - Bucket: {S3_BUCKET}, Key: results/{request_id}.json")
    
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f'results/{request_id}.json',
        Body=json.dumps(data, default=str),
        ContentType='application/json'
    )
    
    logger.info(f"Successfully saved error to S3 for request_id: {request_id}")
