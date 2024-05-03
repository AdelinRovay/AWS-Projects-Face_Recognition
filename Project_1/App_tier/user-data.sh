#!/bin/bash
sudo apt-get update
sudo apt-get install awscli -y
sudo pip3 install boto3
export PATH=$PATH:/usr/local/bin/aws
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
NEW_INSTANCE_NAME="app-tier-instance-$INSTANCE_ID"
aws ec2 create-tags --resources $INSTANCE_ID --tags "Key=Name,Value=$NEW_INSTANCE_NAME" --region us-east-1
sudo -u ubuntu python3 /home/ubuntu/app-tier/app.py | tee /home/ubuntu/app-tier/logfile.log