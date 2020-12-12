import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

import chp
from chp.trapi_interface import TrapiInterface
import chp_client
import chp_data
import pybkb

from .util import QueryProcessor

# Setup logging
logging.basicConfig(level=20)

# Setup Logger
logger = logging.getLogger(__name__)

class query_all(APIView):

    def post(self, request):
        if request.method == 'POST':
            query_processor = QueryProcessor(request)
            return query_processor.get_response_to_query()

class query(APIView):

    def post(self, request):
        if request.method == 'POST':
            query_processor = QueryProcessor(request)
            return query_processor.get_response_to_query()

class check_query(APIView):

    def post(self, request):
        if request.method == 'POST':
            query, max_results, client_id = QueryProcessor._process_request(request)

            # Instaniate interface
            interface = TrapiInterface(query=query, client_id=client_id)

            return JsonResponse(interface.check_query())

class curies(APIView):
    
    def get(self, request):
        if request.method == 'GET':
            query, max_results, client_id = QueryProcessor._process_request(request)

            # Instaniate interface
            interface = TrapiInterface(client_id=client_id)

            # Get supported curies
            curies = interface.get_curies()

            return JsonResponse(curies)

class predicates(APIView):
    
    def get(self, request):
        if request.method == 'GET':
            query, max_results, client_id = QueryProcessor._process_request(request)

            # Instaniate interface
            interface = TrapiInterface(client_id=client_id)

            # Get supported predicates
            predicates = interface.get_predicates()
            return JsonResponse(predicates)

class versions(APIView):

    def get(self, request):
        if request.method == 'GET':
            versions = { 'chp' : chp.__version__,
                         'chp_client' : chp_client.__version__,
                         'chp_data' : chp_data.__version__,
                         'pybkb' : pybkb.__version__ }
        return JsonResponse(versions)
