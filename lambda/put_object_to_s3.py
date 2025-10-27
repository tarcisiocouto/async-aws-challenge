import os
import boto3
import json
from dotenv import load_dotenv
import random

load_dotenv()

BUCKET_NAME = os.getenv('BUCKET_NAME')

def put_object():
    id = random.randint(10000, 99999)
    message = {
        'id': str(id),
        'message': 'Hello, this is a test object for S3!',
        'status': 'success',
        'code': 200
    }
    message_parsed = json.dumps(message).encode('utf-8')
    amazon_s3 = boto3.client('s3')
    amazon_s3.put_object(Bucket=BUCKET_NAME, Key=f'{message["id"]}.txt', Body=message_parsed)


if __name__ == "__main__":
    put_object()