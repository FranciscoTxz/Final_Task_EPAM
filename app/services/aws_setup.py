import boto3
from app.config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)
