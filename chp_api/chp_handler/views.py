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

    def post(self, request):
        if request.method == 'POST':
            data = request.data

            query = data['query']
            source_ara = query['reasoner_id']

            handler = ReasonerStdHandler(source_ara, dict_query=query)
            handler.buildChpQueries()
            handler.runChpQueries()

            response = handler.constructDecoratedKG()

            return JsonResponse(response)

class check_query(APIView):

    def post(self, request):
        if request.method == 'POST':
            data = request.data

            query = data['query']
            source_ara = query['reasoner_id']

            handler = ReasonerStdHandler(source_ara, dict_query=query)

            return JsonResponse(handler.checkQuery())

class get_supported_node_types(APIView):
    
    def get(self, request):
        if requests.method == 'GET':
            return JsonResponse(None)

class get_supported_edge_types(APIView):
    
    def get(self, request):
        if requests.method == 'GET':
            return JsonResponse(None)

