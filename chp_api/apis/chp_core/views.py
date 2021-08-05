""" CHP Core API Views
"""
from jsonschema import ValidationError
from copy import deepcopy

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import chp
import chp_client
import chp_data
import pybkb

from chp.trapi_interface import TrapiInterface
from trapi_model.processing_and_validation.metakg_validation_exceptions import UnsupportedPrefix

from utils.trapi import ChpCoreQueryProcessor

class query(APIView):
    trapi_version = '1.1'

    def post(self, request):
        if request.method == 'POST':
            try:
                data_copy = deepcopy(request.data)
                query_processor = ChpCoreQueryProcessor(request, self.trapi_version)
            except UnsupportedPrefix as e:
                response = { 'query_graph' : data_copy['message']["query_graph"],
                     'knowledge_graph' : { 'edges': dict(), 'nodes': dict()},
                     'results': [] }
                message = {'message' : response,
                        'description' : 'Unsupported query',
                        'status': 'Bad Request. ' + str(e)}
                return JsonResponse(message, status=400) 
            except Exception as e:
                response = { 'query_graph' : data_copy['message']["query_graph"],
                     'knowledge_graph' : { 'edges': dict(), 'nodes': dict()},
                     'results': [] }
                message = {'message' : response,
                        'description' : 'Unsupported query',
                        'status': 'Bad Request. ' + str(e)}
                return JsonResponse(message) 
            return query_processor.get_response_to_query()

class curies(APIView):
    trapi_version = '1.1'
    
    def get(self, request):
        if request.method == 'GET':
            # Instaniate interface
            interface = TrapiInterface()

            # Get supported curies
            curies = interface.get_curies()

            return JsonResponse(curies)

class meta_knowledge_graph(APIView):
    trapi_version = '1.1'

    def get(self, request):
        if request.method == 'GET':
            interface = TrapiInterface()
            meta_knowledge_graph = interface.get_meta_knowledge_graph()
            return JsonResponse(meta_knowledge_graph.json())

class versions(APIView):
    trapi_version = '1.1'

    def get(self, request):
        if request.method == 'GET':
            versions = { 'chp' : chp.__version__,
                         'chp_client' : chp_client.__version__,
                         'chp_data' : chp_data.__version__,
                         'pybkb' : pybkb.__version__ }
        return JsonResponse(versions)
