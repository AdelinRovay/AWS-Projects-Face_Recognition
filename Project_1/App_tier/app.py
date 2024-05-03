import boto3
import config as config
import subprocess
import os
import json
import sys
import time


session = boto3.Session(
	region_name="us-east-1",
	aws_access_key_id=config.ACCESS_KEY,
	aws_secret_access_key=config.SECRET_KEY
)

sqs = session.client('sqs')
s3 = session.resource('s3')

os.chdir("/home/ubuntu/")

def get_message():

	response = sqs.receive_message(
		QueueUrl=config.REQ_SQS_QUEUE_URL,
		MaxNumberOfMessages=config.SQS_MAX_NUMBER_OF_MESSAGES,
		VisibilityTimeout=config.SQS_VISIBILITY_TIMEOUT,
		WaitTimeSeconds=config.SQS_WAIT_TIME_SECONDS
	)

	if "Messages" not in response:
		print("No message received")
		return
	
	request_index = 0
	message_body = response["Messages"][0]["Body"]

	message_body = json.loads(message_body)

	receipt_handle = response["Messages"][0]["ReceiptHandle"]

	file_name = message_body["image_url"].split("/")[-1]
	request_id = message_body["request_id"]

	response_queue_messages = sqs.receive_message(
		QueueUrl=config.RES_SQS_QUEUE_URL,
		MaxNumberOfMessages=config.SQS_MAX_NUMBER_OF_MESSAGES,
		VisibilityTimeout=config.SQS_VISIBILITY_TIMEOUT,
		WaitTimeSeconds=config.SQS_WAIT_TIME_SECONDS
	)

	if "Messages" in response_queue_messages:
		flag = 1
		while(flag):
				flag = 0
				for i in range(response["Messages"]):
					response_id = json.loads(response["Messages"][i]["Body"])["request_id"]
					if response_id ==  request_id:
						flag = 1
				if flag:
					request_index += 1
					message_body = response["Messages"][request_index]["Body"]
					message_body = json.loads(message_body)
					receipt_handle = response["Messages"][request_index]["ReceiptHandle"]
					file_name = message_body["image_url"].split("/")[-1]
					request_id = message_body["request_id"]
			



	image_name = file_name.rsplit('.', maxsplit=1)[0]

	try:
		s3.meta.client.download_file(config.INPUT_S3_BUCKET_NAME, file_name, f"../model/{file_name}")
		print("File downloaded successfully.")
	except Exception as e:
		print(f"Error: {str(e)}")


	# piece of code that executes the python script
	working_directory = os.path.dirname(__file__)
	command = ["python3", "/home/ubuntu/cloud/model/face_recognition.py", file_name]
	result = subprocess.run(command, stdout=subprocess.PIPE,
	                        stderr=subprocess.PIPE, text=True, cwd=working_directory)

	output = result.stdout

	if not output:
		print("The output is empty/false")

	print("Image : {}".format(image_name), "Result : {}".format(output))

	message_json = {
		"output": output,
		"request_id": request_id
	}

	message_json = json.dumps(message_json)

	# # Sending the result back in the response queue for the controller to consume/print
	sqs.send_message(
		QueueUrl=config.RES_SQS_QUEUE_URL,
		MessageBody=message_json,
	)

	# storing the result as key/value pair in s3 for persistence
	s3.meta.client.put_object(Body=output.encode('utf-8'),
	              Bucket=config.OUTPUT_S3_BUCKET_NAME, Key=image_name)

	## delete the message from the sqs queue
	sqs.delete_message(
		QueueUrl=config.REQ_SQS_QUEUE_URL,
		ReceiptHandle=receipt_handle
	)

	# delete the file in the local
	os.remove(f"/home/ubuntu/cloud/model/{file_name}")

while True:
	print("running..")
	get_message()
	time.sleep(5)
	sys.stdout.flush()