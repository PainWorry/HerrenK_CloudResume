import json
import boto3
import os

def lambda_handler(event, context):
    
    # Connection logic MUST be inside the handler.
    table_name = os.environ.get('TABLE_NAME', 'cloud-resume-views')
    region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'ap-southeast-2'
    
    dynamodb_client = boto3.resource('dynamodb', region_name=region)
    table = dynamodb_client.Table(table_name)

    try:
        # Get the 'id' (partition key) to update. We'll use '0' as a static ID.
        item_id = '0'
        
        # --- THIS IS THE FIX for the 'views' reserved keyword ---
        response = table.update_item(
            Key={'id': item_id},
            # Use #v as a placeholder for 'views'
            UpdateExpression='ADD #v :inc',
            ExpressionAttributeNames={
                '#v': 'views'
            },
            # --- END OF FIX ---
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
        print(f"LAMBDA HANDLER FAILED: {e}")
        
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