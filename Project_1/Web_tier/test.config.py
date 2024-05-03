#AWS Credentials
REGION="us-east-1"
ACCESS_KEY="AKIA47CRULZZSYQGMV4A"
SECRET_KEY="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"

#AWS SQS
REQ_SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/891376918131/1230434246-req-queue"
RES_SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/891376918131/1230434246-resp-queue"
SQS_MAX_NUMBER_OF_MESSAGES=10
SQS_VISIBILITY_TIMEOUT=0
SQS_WAIT_TIME_SECONDS=10

#AWS S3
INPUT_S3_BUCKET_NAME="1230434246-in-bucket"
OUTPUT_S3_BUCKET_NAME="1230434246-out-bucket"

#codes
RES_NOT_FOUND_CODE = "message not found yet"
SQS_ERROR_CODE = "error in pushing to req SQS"
#AWS EC2
AMI_ID="ami-0fedaea8025c34f4f"
INSTANCE_TYPE="t2.micro"

#AWS Auto Scaling Group
ASG_NAME = "app-tier-asg"