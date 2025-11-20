import json
import boto3
import os

def lambda_handler(event, context):
    
    # Connection logic MUST be inside the handler.
    # This ensures it runs *after* test fixtures set the env vars
    # and handles Lambda's cold start behavior correctly.
    table_name = os.environ.get('TABLE_NAME', 'cloud-resume-views')
    region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'ap-southeast-2'
    
    dynamodb_client = boto3.resource('dynamodb', region_name=region)
    table = dynamodb_client.Table(table_name)

    try:
        item_id = '0'
        
        # We hit a bug here: 'views' is a reserved keyword in DynamoDB.
        # The fix is to use an ExpressionAttributeName placeholder (#v).
        response = table.update_item(
            Key={'id': item_id},
            # Use #v as a placeholder for 'views'
            UpdateExpression='ADD #v :inc',
            ExpressionAttributeNames={
                '#v': 'views' 
            },
            ExpressionAttributeValues={':inc': 1},
            ReturnValues='UPDATED_NEW'
        )
        
        view_count = response['Attributes']['views']
        
        # Return a successful, CORS-enabled response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', # Allow our website
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps({'views': str(view_count)})
        }
    
    except Exception as e:
        # Print the real error to CloudWatch logs for debugging
        print(f"LAMBDA HANDLER FAILED: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps({'error': str(e)})
        }