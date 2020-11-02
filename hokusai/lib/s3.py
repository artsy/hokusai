import botocore
import boto3

from hokusai.lib.common import get_region_name

def append_or_create_object(data, s3_bucket, s3_key):
  s3_client = boto3.client('s3', region_name=get_region_name())

  # let upstream handle exceptions.
  if object_exists(s3_client, s3_bucket, s3_key):
    append_to_object(s3_client, data, s3_bucket, s3_key)
  else:
    create_object(s3_client, data, s3_bucket, s3_key)

def object_exists(s3_client, s3_bucket, s3_key):
  try:
    s3_client.head_object(Bucket=s3_bucket, Key=s3_key)
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      # catch the case where key does not exist.
      return False
    else:
      # some other exception, pass it upstream.
      raise

  # key exists.
  return True
  
def create_object(s3_client, data, s3_bucket, s3_key):
  # let upstream handle exceptions.
  s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=data)

def append_to_object(s3_client, data, s3_bucket, s3_key):
  # let upstream handle exceptions.
  response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
  new_data = response['Body'].read() + data
  s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=new_data)

