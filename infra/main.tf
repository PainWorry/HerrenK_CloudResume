# Get your AWS Account ID and Region automatically
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# --- IAM Role and Policy ---

# 1. Create the IAM Role for the Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "cloud-resume-lambda-role"
  
  # Policy that allows Lambda to assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# 2. Create the IAM Policy to allow access to DynamoDB
resource "aws_iam_policy" "dynamodb_policy" {
  name        = "cloud-resume-dynamodb-policy"
  description = "Allows Lambda to Get/Update items in the DynamoDB table"
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "dynamodb:UpdateItem",
          "dynamodb:GetItem"
        ],
        Effect   = "Allow",
        # This dynamically gets your account ID, region, and the table name
        Resource = "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${aws_dynamodb_table.visitor_table.name}"
      }
    ]
  })
}

# 3. Attach the DynamoDB policy to the Lambda role
resource "aws_iam_role_policy_attachment" "dynamodb_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
}

# 4. Attach the basic Lambda execution policy (for CloudWatch Logs)
resource "aws_iam_role_policy_attachment" "lambda_logs_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# --- Lambda Function ---

# 5. Zip up the Python code from the 'lambda' folder
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

# 6. Create the Lambda Function
resource "aws_lambda_function" "visitor_counter" {
  function_name = "cloud-resume-visitor-counter"
  handler       = "func.lambda_handler" # File is 'func.py', function is 'lambda_handler'
  runtime       = "python3.10"
  role          = aws_iam_role.lambda_role.arn

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  # Pass the DynamoDB table name to the Lambda as an environment variable
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.visitor_table.name
    }
  }
}

# 7. Create the public Function URL for the Lambda
resource "aws_lambda_function_url" "visitor_counter_url" {
  function_name      = aws_lambda_function.visitor_counter.function_name
  authorization_type = "NONE" # Make it public

  # Configure CORS to allow your website to call it
  cors {
    allow_credentials = true
    allow_origins     = ["*"] # Allows all origins
    allow_methods     = ["GET"]
    allow_headers     = ["*"]
  }
}

# --- Outputs ---

# 8. Print the new Lambda URL in the terminal after it's created
output "lambda_function_url" {
  description = "The public URL for the visitor counter Lambda function"
  value       = aws_lambda_function_url.visitor_counter_url.function_url
}