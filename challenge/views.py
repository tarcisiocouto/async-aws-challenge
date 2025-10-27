import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .services import ProductService
from .selectors import ProductSelectors


class ProductAPIView(APIView):
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_service = ProductService()
        self.product_selector = ProductSelectors()

    def post(self, request):
        response = self.product_service.call_lambda_aws(request)
        return Response(response, status=status.HTTP_201_CREATED)
    
    def get(self, request, id):
        data = self.product_selector.select_product_by_id(id)
        # Verifica se o seletor retornou um dicionário de erro
        if 'error' in data:
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(data, status=status.HTTP_200_OK)