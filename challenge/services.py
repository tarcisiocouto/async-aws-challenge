import os
import requests
from .serializers import ProductSerializer


class ProductService:

    def __init__(self):
        self._lambda_aws_url = os.getenv("LAMBDA_FUNCTION_AWS_URL", "")

    def call_lambda_aws(self, request):
        response = requests.post(self._lambda_aws_url, json=request.data)
        return response.json()
    
    def create_product(self, request):
        # Logic to create a product
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        else:
            return serializer.errors