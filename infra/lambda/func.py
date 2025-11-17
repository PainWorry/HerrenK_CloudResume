import json
import boto3
import os

# Get the DynamoDB table name from an environment variable
TABLE_NAME = os.environ.get('TABLE_NAME', 'cloud-resume-views')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Get the 'id' (partition key) to update. We'll use '0' as a static ID.
        item_id = '0'
        
        # Update the item in DynamoDB and return the new value
        response = table.update_item(
            Key={'id': item_id},
            UpdateExpression='ADD views :inc',
            ExpressionAttributeValues={':inc': 1},
            ReturnValues='UPDATED_NEW'
        )
        
        # Get the new view count from the response
        view_count = response['Attributes']['views']
        
        # Return a successful, CORS-enabled response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps({'views': str(view_count)})
        }
    
    except Exception as e:
        # Handle any errors and return a CORS-enabled error response
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps({'error': str(e)})
        }