# Get account/region data automatically
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# 1. Create the IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "cloud-resume-lambda-role"
  # This policy allows Lambda to "assume" this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

# 2. Create the DynamoDB Policy
resource "aws_iam_policy" "dynamodb_policy" {
  name   = "cloud-resume-dynamodb-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["dynamodb:UpdateItem", "dynamodb:GetItem"],
        Effect   = "Allow",
        # This dynamically builds the ARN for our table
        Resource = "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${aws_dynamodb_table.visitor_table.name}"
      }
    ]
  })
}

# 3. Attach policies to the role
resource "aws_iam_role_policy_attachment" "dynamodb_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
}
# This policy allows writing logs to CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_logs_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 4. Zip up the Python code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

# 5. Create the Lambda Function
resource "aws_lambda_function" "visitor_counter" {
  function_name = "cloud-resume-visitor-counter"
  handler       = "func.lambda_handler" # (filename.function_name)
  runtime       = "python3.10" # Choose a runtime
  role          = aws_iam_role.lambda_role.arn

  # Upload the code
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  # Pass the table name as an Environment Variable
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.visitor_table.name
    }
  }
}

# 6. Create the public Function URL
resource "aws_lambda_function_url" "visitor_counter_url" {
  function_name      = aws_lambda_function.visitor_counter.function_name
  authorization_type = "NONE" # Make it public
  cors {
    allow_origins = ["*"] # Allow all origins (for this project)
    allow_methods = ["GET"]
  }
}

# 7. Print the URL to the terminal
output "lambda_function_url" {
  description = "The public URL for the visitor counter"
  value       = aws_lambda_function_url.visitor_counter_url.function_url
}