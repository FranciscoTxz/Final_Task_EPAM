from fastapi import UploadFile
from app.services.aws_setup import s3_client, AWS_BUCKET_NAME, AWS_REGION
import uuid


async def upload_file_to_s3(file: UploadFile) -> str:
    """Upload a file to S3 and return the URL"""
    try:
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Upload file
        s3_client.upload_fileobj(
            file.file,
            AWS_BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ACL": "public-read"},
        )

        # Generate URL
        url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        return url

    except Exception as e:
        raise Exception(f"Error uploading file to S3: {str(e)}")


async def delete_file_from_s3(url: str) -> bool:
    """Delete a file from S3 using its URL"""
    try:
        # Extract key from URL
        key = url.split("/")[-1]

        # Delete file
        s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=key)
        return True

    except Exception as e:
        raise Exception(f"Error deleting file from S3: {str(e)}")
