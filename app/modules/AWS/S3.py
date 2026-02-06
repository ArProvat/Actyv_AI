from app.config.settings import settings
import boto3

class S3_Manager:
     def __init__(self):
          self.s3 = boto3.client("s3",
          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
          region_name=settings.AWS_REGION_NAME)
     
     async def upload_file(self,file_path:str,file_name:str):
          try:
               self.s3.upload_file(file_path,settings.AWS_S3_BUCKET_NAME,file_name)
               return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{file_name}"
          except Exception as e:
               print(e)
               return None
     
     async def upload_file_from_bytes(self,file_bytes:bytes,):
          try:
               file_name = f"images/AI_coach/{uuid.uuid4()}.png"
               self.s3.put_object(Bucket=settings.AWS_S3_BUCKET_NAME,Key=file_name,Body=file_bytes)
               return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{file_name}"
          except Exception as e:
               print(e)
               return None