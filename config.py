import os
from dotenv import load_dotenv

load_dotenv()

AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL")
