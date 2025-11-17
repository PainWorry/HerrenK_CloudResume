terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  # This will use your default AWS CLI profile.
  # If you use a named profile, change "default".
  profile = "default"
  region  = "ap-southeast-2" # Your region
}