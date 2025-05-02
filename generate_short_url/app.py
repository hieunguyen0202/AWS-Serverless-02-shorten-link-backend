import boto3
import random
import string
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# This function receives the original URL and generates a short URL
# Request body json need to contain attribute: "url"
# Sample request body (JSON): 
# {
#   "url": "https://www.example.com"
# }
def lambda_handler(event, context):
    logger.info('Event structure: ' + json.dumps(event))

    body = None
    if 'body' in event and event['body'] is not None:
        try:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'status': 'error', 'message': 'Invalid JSON format'})
            }
    elif 'url' in event:  # This is for test event directly using {"url": "..."}
        body = event
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'status': 'error', 'message': 'Request body is missing'})
        }

    original_url = body.get('url')
    if not original_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'status': 'error', 'message': 'URL is required'})
        }

    # Generate short URL
    short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=15))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UrlShortenTable')

    try:
        table.put_item(
            Item={
                'short_url': short_url,
                'original_url': original_url
            }
        )
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            },
            'body': json.dumps({'short_url_code': short_url})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'status': 'error', 'message': str(e)})
        }