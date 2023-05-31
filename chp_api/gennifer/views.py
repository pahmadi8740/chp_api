import requests

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Dataset, InferenceStudy, InferenceResult, Algorithm
from .serializers import DatasetSerializer, InferenceStudySerializer, InferenceResultSerializer
from .tasks import create_task

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['upload_user', 'zenodo_id']
    permission_classes = [IsAuthenticated]


class InferenceStudyViewSet(viewsets.ModelViewSet):
    serializer_class = InferenceStudySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_public', 'dataset', 'algorithm_instance']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return InferenceStudy.objects.filter(user=user)


class InferenceResultViewSet(viewsets.ModelViewSet):
    serializer_class = InferenceResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_public', 'study', 'tf', 'target']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return InferenceResult.objects.filter(user=user)


class run(APIView):
    
    def post(self, request):
        """ Request comes in as a list of algorithms to run.
        """
        # Build gennifer requests
        tasks = request.data['tasks']
        response = {"tasks": []}
        for task in tasks:
            algorithm_name = task.get("algorithm_name", None)
            zenodo_id = task.get("zenodo_id", None)
            hyperparameters = task.get("hyperparameters", None)
            if hyperparameters:
                if len(hyperparameters) == 0:
                    hyperparameters = None
            if not algorithm_name:
                task["error"] = "No algorithm name provided."
                response["tasks"].append(task)
                continue
            if not zenodo_id:
                task["error"] = "No dataset Zenodo identifer provided."
                response["tasks"].append(task)
                continue
            try:
                algo = Algorithm.objects.get(name=algorithm_name)
            except ObjectDoesNotExist:
                task["error"] = f"The algorithm: {algorithm_name} is not supported in Gennifer." 
                response["tasks"].append(task)
                continue
            # If all pass, now send to gennifer services
            task["task_id"] = create_task.delay(algo.name, zenodo_id, hyperparameters, request.user.pk).id
            response["tasks"].append(task)
        return JsonResponse(response)
