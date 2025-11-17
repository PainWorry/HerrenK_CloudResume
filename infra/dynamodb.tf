# Define the DynamoDB table for view counts
resource "aws_dynamodb_table" "visitor_table" {
  # This is the name your Lambda function will use
  name         = "cloud-resume-views" 
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  # Define the 'id' attribute as a String (S)
  attribute {
    name = "id"
    type = "S"
  }
}