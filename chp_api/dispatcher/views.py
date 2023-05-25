""" CHP Core API Views
"""
from jsonschema import ValidationError
from copy import deepcopy
from datetime import datetime, timedelta

from .base import Dispatcher
from .models import Transaction, DispatcherSettings
from .serializers import TransactionListSerializer, TransactionDetailSerializer

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics


class query(APIView):
    
    def post(self, request):
        # Get current trapi and biolink versions
        dispatcher_settings = DispatcherSettings.load()
        
        if request.method == 'POST':
            # Initialize Dispatcher
            dispatcher = Dispatcher(
                    request,
                    dispatcher_settings.trapi_version,
                    )
            # Process Query
            query = None
            #try:
            query = dispatcher.process_request(
                    request,
                    trapi_version=dispatcher_settings.trapi_version,
                    )
            #except Exception as e:
            #    if 'Workflow Error' in str(e):
            #        return dispatcher.process_invalid_workflow(request, str(e))
            #    else:
            #        return dispatcher.process_invalid_trapi(request)
            # Return responses
            return dispatcher.get_response(query)

class meta_knowledge_graph(APIView):
    
    def get(self, request):
        # Get current trapi and biolink versions
        dispatcher_settings = DispatcherSettings.load()
        
        if request.method == 'GET':
            # Initialize Dispatcher
            dispatcher = Dispatcher(
                    request,
                    dispatcher_settings.trapi_version,
                    )
            
            # Get merged meta KG
            meta_knowledge_graph = dispatcher.get_meta_knowledge_graph()
            return JsonResponse(meta_knowledge_graph.to_dict())

class versions(APIView):

    def get(self, request):
        # Get current trapi and biolink versions
        dispatcher_settings = DispatcherSettings.load()
        
        if request.method == 'GET':
            # Initialize Dispatcher
            dispatcher = Dispatcher(
                    request,
                    dispatcher_settings.trapi_version,
                    )
        return JsonResponse(dispatcher.get_versions())

class TransactionList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class RecentTransactionList(mixins.ListModelMixin, generics.GenericAPIView):
    date_from = datetime.now() - timedelta(days=1)
    queryset = Transaction.objects.filter(date_time__gte=date_from).order_by('-date_time')
    serializer_class = TransactionListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class TransactionDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionDetailSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
