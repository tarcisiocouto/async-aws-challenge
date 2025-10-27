import os
import boto3
import uuid
from dotenv import load_dotenv

load_dotenv()

dynamo_cliente = boto3.client("dynamodb")

table_name = os.getenv("DYNAMODB_TABLE_NAME", "")

product_id = str(uuid.uuid4())

message_body = {
    "product_id": product_id,
    "name": "Sample Product",
    "description": "This is a sample product.",
    "price": 19.99,
}

dynamo_cliente.put_item(TableName=table_name, Item={
    "id": {"S": message_body["product_id"]},
    "name": {"S": message_body["name"]},
    "description": {"S": message_body["description"]},
    "price": {"N": str(message_body["price"])},
})