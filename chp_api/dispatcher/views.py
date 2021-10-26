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

from dispatcher import Dispatcher

class query(APIView):
    trapi_version = '1.2'
    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(query, self).__init__(**kwargs)

    def post(self, request):
        if request.method == 'POST':
            # Initialize Dispatcher
            dispatcher = Dispatcher(request, self.trapi_version)
            # Process Query
            query = None
            try:
                query = dispatcher.process_request(request, trapi_version=self.trapi_version)
            except Exception as e:
                if 'Workflow Error' in str(e):
                    return dispatcher.process_invalid_workflow(request, str(e))
                else:
                    return dispatcher.process_invalid_trapi(request)
            # Return responses
            return dispatcher.get_response(query)

class curies(APIView):
    trapi_version = '1.2'
    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(curies, self).__init__(**kwargs)
    
    def get(self, request):
        if request.method == 'GET':
            # Initialize dispatcher
            dispatcher = Dispatcher(request, self.trapi_version)

            # Get all chp app curies
            curies_db = dispatcher.get_curies()

            return JsonResponse(curies_db)

class meta_knowledge_graph(APIView):
    trapi_version = '1.2'
    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(meta_knowledge_graph, self).__init__(**kwargs)

    def get(self, request):
        if request.method == 'GET':
            # Initialize Dispatcher
            dispatcher = Dispatcher(request, self.trapi_version)
           
            # Get merged meta KG
            meta_knowledge_graph = dispatcher.get_meta_knowledge_graph()
            return JsonResponse(meta_knowledge_graph.to_dict())

class versions(APIView):
    trapi_version = '1.2'
    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(version, self).__init__(**kwargs)

    def get(self, request):
        if request.method == 'GET':
            # Initialize Dispatcher
            dispatcher = Dispatcher(request, self.trapi_version)
        return JsonResponse(dispatcher.get_versions())

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
