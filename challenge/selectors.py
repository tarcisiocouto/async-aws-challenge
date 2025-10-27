import os
import requests
import json
from dotenv import load_dotenv
from .serializers import ProductSerializer

load_dotenv()


class ProductSelectors:

    def __init__(self) -> None:
        self._lambda_url = os.getenv('LAMBDA_FUNCTION_AWS_URL_GET_PRODUCT')
    
    def select_product_by_id(self, id: str):
        response = requests.get(f'{self._lambda_url}?id={id}')
        return response.json()