from django.shortcuts import render
from .apps import ChpHandlerConfig

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chp.core.reasoner_std import ReasonerStdHandler

class submit_query(APIView):

    def get(self, request):
        if request.method == 'GET':
            params = request.GET.get('query')

            source_ara = query['reasoner_id']

            handler = ReasonerStdHandler(source_ara, json_query=params)
            handler.buildQueries()
            handler.runQueries()

            response = handler.constructDecoratedKG()

            return JsonResponse(response)

class check_query(APIView):

    def get(self, request):
        if request.method == 'GET':
            params = request.GET.get('query')

            source_ara = params['reasoner_id']

            handler = ReasonerStdHandler(source_ara, json_query=params)
            return JsonResponse(handler.checkQuery())

class get_supported_node_types(APIView):
    
    def get(self, request):
        if requests.method == 'GET':
            return JsonResponse(None)

class get_supported_edge_types(APIView):
    
    def get(self, request):
        if requests.method == 'GET':
            return JsonResponse(None)

