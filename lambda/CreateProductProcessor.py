import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL")


sqs_client = boto3.client("sqs")

message_body = {
    "product_id": "12345",
    "name": "Sample Product",
    "description": "This is a sample product.",
    "price": 19.99,
}

response = sqs_client.send_message(
    QueueUrl=AWS_SQS_QUEUE_URL, MessageBody=json.dumps(message_body)
)

print("Message sent to SQS:", response.get("MessageId"))
