import pytest
import boto3
import os
from moto import mock_aws  # Use the new, correct mock
from func import lambda_handler # This imports your fixed function

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'ap-southeast-2'
    # Set the table name for our tests
    os.environ['TABLE_NAME'] = 'test-table'

# This fixture automatically starts/stops the AWS mock for every test
@pytest.fixture(autouse=True)
def auto_mock_aws(aws_credentials):
    """Auto-starts mock_aws for all tests."""
    with mock_aws():
        yield

@pytest.fixture
def dynamodb_table(aws_credentials):
    """Create a mock DynamoDB table."""
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    
    table = dynamodb.create_table(
        TableName='test-table',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )
    # Add the starting item
    table.put_item(Item={'id': '0', 'views': 0})
    return table

def test_lambda_handler(dynamodb_table):
    """Test the lambda_handler function."""
    
    # Call the lambda_handler
    event = {}
    context = {}
    response = lambda_handler(event, context)
    
    # Check the response
    assert response['statusCode'] == 200
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    assert '"views": "1"' in response['body'] # It should be 1 after the first call

    # Call it a second time to see if it increments
    response = lambda_handler(event, context)
    assert response['statusCode'] == 200
    assert '"views": "2"' in response['body'] # It should be 2 after the second call