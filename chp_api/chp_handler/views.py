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
import trapi_model.biolink as tp
import pybkb
from copy import deepcopy

from trapi_model.processing_and_validation.metakg_validation_exceptions import UnsupportedPrefix

from jsonschema import ValidationError


from .util import QueryProcessor

class query_all(APIView):
    trapi_version = '1.1'
    #def __init__(self, trapi_version='1.1', **kwargs):
    #    self.trapi_version = trapi_version
    #    super(query_all, self).__init__(**kwargs)

    def post(self, request):
        if request.method == 'POST':
            try:
                data_copy = deepcopy(request.data)
                query_processor = QueryProcessor(request, self.trapi_version)
            except UnsupportedPrefix as e:
                response = { 'query_graph' : data_copy['message']["query_graph"],
                     'knowledge_graph' : { 'edges': dict(), 'nodes': dict()},
                     'results': [] }
                message = {'message' : response,
                        'description' : 'Unsupported query',
                        'status': 'Bad Request. ' + str(e)}
            except ValidationError as e:
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
            return query_processor.get_response_to_query()

class query(APIView):
    trapi_version = '1.1'
    #def __init__(self, trapi_version='1.1', **kwargs):
    #    self.trapi_version = trapi_version
    #    super(query, self).__init__(**kwargs)

    def post(self, request):
        if request.method == 'POST':
            try:
                data_copy = deepcopy(request.data)
                query_processor = QueryProcessor(request, self.trapi_version)
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


class check_query(APIView):
    trapi_version = '1.1'
    #def __init__(self, trapi_version='1.1', **kwargs):
    #    self.trapi_version = trapi_version
    #    super(check_query, self).__init__(**kwargs)

    def post(self, request):
        if request.method == 'POST':
            #query, max_results, client_id = QueryProcessor._process_request(
            #        request,
            #        self.trapi_version,
            #        )

            # Instaniate interface
            interface = TrapiInterface()

            return JsonResponse(interface.check_query())

class curies(APIView):
    trapi_version = '1.1'
    #def __init__(self, trapi_version='1.1', **kwargs):
    #    self.trapi_version = trapi_version
    #    super(curies, self).__init__(**kwargs)
    
    def get(self, request):
        if request.method == 'GET':
            #query, max_results, client_id = QueryProcessor._process_request(
            #        request,
            #        self.trapi_version,
            #        )

            # Instaniate interface
            interface = TrapiInterface()

            # Get supported curies
            curies = interface.get_curies()

            return JsonResponse(curies)

class predicates(APIView):
    trapi_version = '1.1'
    #def __init__(self, trapi_version='1.1', **kwargs):
    #    self.trapi_version = trapi_version
    #    super(predicates, self).__init__(**kwargs)
    
    def get(self, request):
        if request.method == 'GET':
            #query, max_results, client_id = QueryProcessor._process_request(
            #        request,
            #        self.trapi_version,
            #        )

            # Instaniate interface
            interface = TrapiInterface()

            # Get supported predicates
            predicates = interface.get_predicates()
            return JsonResponse(predicates)

class meta_knowledge_graph(APIView):
    trapi_version = '1.1'

    def get(self, request):
        if request.method == 'GET':
            interface = TrapiInterface()
            meta_knowledge_graph = interface.get_meta_knowledge_graph()
            return JsonResponse(meta_knowledge_graph)

class versions(APIView):
    trapi_version = '1.1'
    #def __init__(self, trapi_version='1.1', **kwargs):
    #    self.trapi_version = trapi_version
    #    super(versions, self).__init__(**kwargs)

    def get(self, request):
        if request.method == 'GET':
            versions = { 'chp' : chp.__version__,
                         'chp_client' : chp_client.__version__,
                         'chp_data' : chp_data.__version__,
                         'pybkb' : pybkb.__version__ }
        return JsonResponse(versions)

class constants(APIView):
    trapi_version = '1.1'
    #def __init__(self, trapi_version='1.1', **kwargs):
    #    self.trapi_version = trapi_version
    #    super(constants, self).__init__(**kwargs)

    def get(self, request):
        if request.method == 'GET':
            constants = {}
            for var, value in vars(tp.trapi_constants).items():
                if 'BIOLINK' in var:
                    constants[var] = value
        return JsonResponse(constants)
