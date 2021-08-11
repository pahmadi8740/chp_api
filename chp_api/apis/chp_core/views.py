""" CHP Core API Views
"""
from jsonschema import ValidationError
from copy import deepcopy

from apis.chp_core.models import Transaction
from apis.chp_core.serializers import TransactionListSerializer, TransactionDetailSerializer

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics

from utils.trapi_query_processor import ChpCoreQueryProcessor

class query(APIView):
    trapi_version = '1.1'

    def post(self, request):
        if request.method == 'POST':
            # Initialize Query Processor
            query_processor = ChpCoreQueryProcessor(request, self.trapi_version)
            # Process Query
            query = query_processor.process_request(request)
            # Return responses
            return query_processor.get_response(query)

class curies(APIView):
    trapi_version = '1.1'
    
    def get(self, request):
        if request.method == 'GET':
            # Initialize Query Processor
            query_processor = ChpCoreQueryProcessor(request, self.trapi_version)
            
            # Get CHP App Config based on subdomain
            chp_config, _ = query_processor.get_app_config(request)

            # Get TRAPI Interface
            interface = query_processor.get_trapi_interface(chp_config)

            # Get supported curies
            curies_db = interface.get_curies()

            return JsonResponse(curies_db.to_dict())

class meta_knowledge_graph(APIView):
    trapi_version = '1.1'

    def get(self, request):
        if request.method == 'GET':
            # Initialize Query Processor
            query_processor = ChpCoreQueryProcessor(request, self.trapi_version)
            
            # Get CHP App Config based on subdomain
            chp_config, _ = query_processor.get_app_config(request)

            # Get TRAPI Interface
            interface = query_processor.get_trapi_interface(chp_config)
            
            # Get Meta KG
            meta_knowledge_graph = interface.get_meta_knowledge_graph()
            return JsonResponse(meta_knowledge_graph.to_dict())

class versions(APIView):
    trapi_version = '1.1'

    def get(self, request):
        if request.method == 'GET':
            # Initialize Query Processor
            query_processor = ChpCoreQueryProcessor(request, self.trapi_version)
        return JsonResponse(query_processor.get_versions())

class TransactionList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class TransactionDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
