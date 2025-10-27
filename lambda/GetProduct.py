import json
import boto3
from dotenv import load_dotenv
import os

load_dotenv()


dynamodb_client = boto3.client('dynamodb')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')

product_id = '2fb05cff-29db-4e54-8512-54e66bf5eb50'  # Example product ID to retrieve

response = dynamodb_client.get_item(
    TableName=DYNAMODB_TABLE_NAME,
    Key={
        'id': {'S': product_id}
    }
)

print(f"Retrieved item: {response}")
print("############")
print(json.dumps(response.get('Item', {}), indent=4))