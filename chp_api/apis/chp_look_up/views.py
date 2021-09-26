from django.shortcuts import render

# Create your views here.
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils import QueryIdentifier

from chp_look_up.trapi_interface import TrapiInterface

class query(APIView):
    def post(self, request):
        query_processor = QueryIdentifier().getQueryProcessor(request=request)
        return query_processor.getResponse()

class meta_knowledge_graph(APIView):
    trapi_version = '1.2'
    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(meta_knowledge_graph, self).__init__(**kwargs)

    def get(self, request):
        if request.method == 'GET':
            # # Initialize Query Processor
            # query_processor = ChpCoreQueryProcessor(request, self.trapi_version)
            
            # # Get CHP App Config based on subdomain
            # chp_config, _ = query_processor.get_app_config(request)

            # # Get TRAPI Interface
            # interface = query_processor.get_trapi_interface(chp_config)
            
            # # Get Meta KG
            # meta_knowledge_graph = interface.get_meta_knowledge_graph()
            # return JsonResponse(meta_knowledge_graph.to_dict())
            print("foo")
            return JsonResponse({"foo":"goo"})