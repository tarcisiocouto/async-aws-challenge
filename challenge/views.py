import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .services import ProductService


class ProductPostAPIView(APIView):
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_service = ProductService()

    def post(self, request):
        response = self.product_service.call_lambda_aws(request)
        return Response(response, status=status.HTTP_201_CREATED)