import os
import time
import multiprocessing

import chp
import chp_client
import chp_data
import pybkb

from django.shortcuts import render
from .apps import ChpHandlerConfig

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chp.trapi_nterface import TrapiInterface

# Get Hosts File if it exists
parent_dir = os.path.dirname(os.path.realpath(__file__))
HOSTS_FILENAME = os.path.join(parent_dir, 'hosts')
NUM_PROCESSES_PER_HOST = multiprocessing.cpu_count()
#if not os.path.exists(HOSTS_FILENAME):
HOSTS_FILENAME = None
NUM_PROCESSES_PER_HOST = 0

# Import the transaction model so that we may store queries and responses
from chp_handler.models import Transaction

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _process_request(request):
    logger.info('Starting query.')
    data = request.data
    query = data.pop('message', None)
    max_results = data.pop('max_results', 10)
    client_id = data.pop('client_id', 'default')
    return query, max_results, client_id

def _get_response_to_query(query):
        start_time = time.time()

        # Instaniate TRAPI Interface
        interface = TrapiInterface(
            query=query,
            hosts_filename=HOSTS_FILENAME,
            num_processes_per_host=NUM_PROCESSES_PER_HOST,
            max_results=max_results,
            client_id=client_id,
        )

        # Build queries
        handler.buildChpQueries()
        logger.info('Built Queries.')
        # Run queries
        handler.runChpQueries()
        logger.info('Completed Reasoning in {} seconds.'.format(time.time() - start_time))

        # Construct Response
        response = handler.constructDecoratedKG()

        #TODO: Cache answer.

        return JsonResponse(response)

class query_all(APIView):

    def post(self, request):
        if request.method == 'POST':
            query, max_results, client_id = _process_request(request)
            return _get_response_to_query(query, max_results, client_id)

class query(APIView):

    def post(self, request):
        if request.method == 'POST':
            query, max_results, client_id = _process_request(request)
            return _get_response_to_query(query, max_results, client_id)

class check_query(APIView):

    def post(self, request):
        if request.method == 'POST':
            query, max_results, client_id = _process_request(request)

            # Instaniate interface
            interface = TrapiInterface(query=query, client_id=client_id)

            return JsonResponse(interface.check_query())

class curies(APIView):
    
    def get(self, request):
        if request.method == 'GET':
            query, max_results, client_id = _process_request(request)

            # Instaniate interface
            interface = TrapiInteadsrface(client_id=client_id)

            # Get supported curies
            curies = interface.get_curies()

            return JsonResponse(curies)

class predicates(APIView):
    
    def get(self, request):
        if request.method == 'GET':
            query, max_results, client_id = _process_request(request)

            # Instaniate interface
            interface = TrapiInterface(client_id=client_id)

            # Get supported predicates
            predicates = interface.get_predicates()
            predicate_map = {
                              'biolink:Gene' : {
                                                'biolink:Disease' : ['biolink:GeneToDiseaseAssociation']
                                               },
                              'biolink:Drug' : {
                                                'biolink:Disease' : ['biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation'],
                                                'biolink:Gene' : ['biolink:ChemicalToGeneAssociation']
                                               },
                              'biolink:Disease' : {
                                                   'biolink:PhenotypicFeature' : ['biolink:DiseaseToPhenotypicFeatureAssociation']
                                                  }
                            }
            return JsonResponse(predicates)

class versions(APIView):

    def get(self, request):
        if request.method == 'GET':
            versions = { 'chp' : chp.__version__,
                         'chp_client' : chp_client.__version__,
                         'chp_data' : chp_data.__version__,
                         'pybkb' : pybkb.__version__ }
        return JsonResponse(versions)
