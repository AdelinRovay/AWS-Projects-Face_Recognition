#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

from boto3 import client as boto3_client

#import ffmpeg
import urllib.parse
#import shutil
import os
#import json
import boto3

from face_recognition_code import face_recognition_function

def handler(event, context):
  """Face recognition Lambda function triggered by S3 object creation.

  Args:
      event: S3 event containing the details of the new object.
      context: Lambda context object.

  Returns:
      None
  """

  # Get the bucket name and image file name from the event
  record = event['Records'][0]['s3']
  bucket = record['bucket']['name']
  key = urllib.parse.unquote_plus(record['object']['key'], encoding='utf-8')

  output_bucket = "1230434246-output"
  image_path = f"/tmp/{key}"
  # Download the image from S3
  s3_client = boto3.client('s3')
  s3_client.download_file(bucket, key, image_path)
  

  # Perform face recognition
  recognized_name = face_recognition_function(image_path)
  

  # Upload the result text file to the output bucket
  #output_bucket_name = "<ASU_ID>-output"  # Replace with your output bucket name
  output_file_name = os.path.splitext(key)[0] + ".txt"

  if recognized_name:  # Check if a name was recognized
      # Upload result text file with recognized name
      with open("/tmp/" + output_file_name, 'w+') as f:
          f.write(recognized_name)
      s3_client.upload_file("/tmp/" + output_file_name, output_bucket, output_file_name)
      
  else:
      print(f"No face recognized in image {key}")
      # You can optionally upload a file indicating no face recognized here

  # Clean up temporary files
  os.remove(image_path)
  if os.path.exists("/tmp/" + output_file_name):  # Only remove if file exists
      os.remove("/tmp/" + output_file_name)

  return None

