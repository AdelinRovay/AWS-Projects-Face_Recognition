# Copyright 2024, VISA Lab
# License: MIT
import os
import json

import boto3
import urllib.parse
import subprocess
#import shutil
#from video_splitting import video_splitting_cmdline


def video_splitting_cmdline(video_filename):
    filename = os.path.basename(video_filename)
    outfile = os.path.splitext(filename)[0] + ".jpg"

    split_cmd = '/opt/ffmpeglib/ffmpeg -i ' + video_filename + ' -vframes 1 ' + '/tmp/' + outfile
    try:
        subprocess.check_call(split_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)

    #fps_cmd = 'ffmpeg -i ' + video_filename + ' 2>&1 | sed -n "s/.*, \\(.*\\) fp.*/\\1/p"'
    #fps = subprocess.check_output(fps_cmd, shell=True).decode("utf-8").rstrip("\n")
    return outfile
    
def invoke_face_recognition(bucket_name, image_key):
    lambda_client = boto3.client('lambda')

    # Corrected payload structure (single record within Records list)
    payload = {"Records": [{"s3": {"bucket": {"name": bucket_name}, "object": {"key": image_key}}}]}

    # Invoke the face recognition Lambda function
    response = lambda_client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:891376918131:function:face-recognition',
        InvocationType='Event',
        Payload=json.dumps(payload)
    )
    print(response) 


def handler(event, context):
    print("Processing video...")


    # Get input file information from S3 event
    record = event['Records'][0]['s3']
    bucket = record['bucket']['name']
    key = urllib.parse.unquote_plus(record['object']['key'], encoding='utf-8')
    output_bucket = "1230434246-stage-1"
    #output_prefix = os.path.splitext(key)[0]
    video_path = f"/tmp/{key}"

    # Download video from S3
    s3_client = boto3.client('s3')
    s3_client.download_file(bucket, key, video_path)


    # Process the video and get output directory
    out_dir = video_splitting_cmdline(video_path)
    print(out_dir)

    # Upload output to S3
    upload_to_s3(out_dir, output_bucket)
    
    invoke_face_recognition(output_bucket, out_dir)

    # Clean up temporary files
    os.remove(video_path)
    #shutil.rmtree("/tmp/"+out_dir)

    
    return {
        'statusCode': 200,
        'body': 'Video frames split and uploaded to S3 bucket successfully.'
    }
    
def upload_to_s3(out_dir, output_bucket):
    s3_client = boto3.client('s3')
    s3_client.upload_file("/tmp/" + out_dir, output_bucket, out_dir)
    print("Upload complete to Stage-1 Bucket")
