import requests

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from .models import (
        Dataset,
        Study,
        Task,
        Result, 
        Algorithm, 
        Gene, 
        UserAnalysisSession
        )
from .serializers import (
        DatasetSerializer,
        StudySerializer, 
        TaskSerializer, 
        ResultSerializer, 
        AlgorithmSerializer, 
        GeneSerializer,
        UserAnalysisSessionSerializer
        )
from .tasks import create_task
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class UserAnalysisSessionViewSet(viewsets.ModelViewSet):
    serializer_class = UserAnalysisSessionSerializer
    #filter_backends = [DjangoFilterBackend]
    #filterset_fields = ['id', 'name', 'is_saved']
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(f'User is {user}')
        return UserAnalysisSession.objects.filter(user=user)
    

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'zenodo_id']
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]


    def perform_create(self, serializers):
        try:
            serializers.save(user=self.request.user)
        except ValueError as e:
            raise ValidationError(str(e))

class StudyViewSet(viewsets.ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudySerializer
    permission_classes = [IsOwnerOrReadOnly]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_public', 'dataset', 'algorithm_instance']
    permission_classes = [IsOwnerOrReadOnly]

    #def get_queryset(self):
    #    user = self.request.user
    #    return InferenceStudy.objects.filter(user=user)


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_public', 'task', 'tf', 'target']
    permission_classes = [IsOwnerOrReadOnly]

    #def get_queryset(self):
    #    user = self.request.user
    #    return InferenceResult.objects.filter(user=user)

class AlgorithmViewSet(viewsets.ModelViewSet):
    serializer_class = AlgorithmSerializer
    queryset = Algorithm.objects.all()
    permissions = [IsAdminOrReadOnly]

class GeneViewSet(viewsets.ModelViewSet):
    serializer_class = GeneSerializer
    queryset = Gene.objects.all()
    permissions = [IsAdminOrReadOnly]


class CytoscapeView(APIView):

    def construct_node(self, gene_obj):
        if gene_obj.variant:
            name = f'{gene_obj.name}({gene_obj.variant})'
            curie = f'{gene_obj.curie}({gene_obj.variant})'
            chp_preferred_curie = f'{gene_obj.chp_preferred_curie}({gene_obj.variant})'
        else:
            name = gene_obj.name
            curie = gene_obj.curie
            chp_preferred_curie = gene_obj.chp_preferred_curie

        node = {
                "data": {
                    "id": str(gene_obj.pk),
                    "name": name,
                    "curie": curie,
                    "chp_preferred_curie": chp_preferred_curie
                    }
                }
        return node, str(gene_obj.pk)
    
    def construct_edge(self, res, source_id, target_id):
        # Normalize edge weight based on the study
        normalized_weight = (res.edge_weight - res.task.min_study_edge_weight) / (res.task.max_study_edge_weight - res.task.min_study_edge_weight)
        directed = res.task.algorithm_instance.algorithm.directed
        edge_tuple = tuple(sorted([source_id, target_id]))
        edge = {
                "data": {
                    "id": str(res.pk),
                    "source": source_id,
                    "target": target_id,
                    "dataset": str(res.task.dataset),
                    "weight": normalized_weight,
                    "algorithm": str(res.task.algorithm_instance),
                    "directed": directed,
                    }
                }
        return edge, edge_tuple, directed

    def add(self, res, nodes, edges, processed_node_ids, processed_undirected_edges):
        # Construct nodes
        tf_node, tf_id = self.construct_node(res.tf)
        target_node, target_id = self.construct_node(res.target)
        # Add nodes if not already added by another result
        if tf_id not in processed_node_ids:
            nodes.append(tf_node)
            processed_node_ids.add(tf_id)
        if target_id not in processed_node_ids:
            nodes.append(target_node)
            processed_node_ids.add(target_id)
        # Add and construct edge
        edge, edge_tuple, edge_is_directed = self.construct_edge(res, tf_id, target_id)
        if edge_is_directed:
            edges.append(edge)
        elif not edge_is_directed and edge_tuple not in processed_undirected_edges:
            edges.append(edge)
            processed_undirected_edges.add(edge_tuple)
        else:
            pass
        return nodes, edges, processed_node_ids, processed_undirected_edges

    def construct_cytoscape_data(self, results):
        nodes = []
        edges = []
        processed_node_ids = set()
        processed_undirected_edges = set()
        elements = []
        # Construct graph
        for res in results:
            nodes, edges, processed_node_ids, processed_undirected_edges  = self.add(
                    res,
                    nodes,
                    edges,
                    processed_node_ids,
                    processed_undirected_edges,
                    )
            elements.extend(nodes)
            elements.extend(edges)
        return {
                "elements": elements
                }

    def get(self, request):
        results = Result.objects.all()
        cyto = self.construct_cytoscape_data(results)
        return JsonResponse(cyto)

    def post(self, request):
        elements = []
        gene_ids = request.data.get("gene_ids", None)
        task_ids = request.data.get("task_ids", None)
        algorithm_ids = request.data.get("algorithm_ids", None)
        dataset_ids = request.data.get("dataset_ids", None)
        cached_inference_result_ids = request.data.get("cached_results", None)

        if not (study_ids and gene_ids) and not (algorithm_ids and dataset_ids and  gene_ids):
            return JsonResponse({"elements": elements})
        
        # Create Filter
        filters = []
        if gene_ids:
            filters.extend(
                    [
                        {"field": 'tf__pk', "operator": 'in', "value": gene_ids},
                        {"field": 'target__pk', "operator": 'in', "value": gene_ids},
                        ]
                    )
        if study_ids:
            filters.append({"field": 'task__pk', "operator": 'in', "value": study_ids})
        if algorithm_ids:
            filters.append({"field": 'task__algorithm_instance__algorithm__pk', "operator": 'in', "value": study_ids})
        if dataset_ids:
            filters.append({"field": 'task__dataset__zenodo_id', "operator": 'in', "value": dataset_ids})

        # Construct Query
        query = Q()
        for filter_item in filters:
            field = filter_item["field"]
            operator = filter_item["operator"]
            value = filter_item["value"]
            query &= Q(**{f'{field}__{operator}': value})

        # Get matching results
        results = Result.objects.filter(query)

        if len(results) == 0:
            return JsonResponse({"elements": elements})
        
        # Exclude results that have already been sent to user
        if cached_inference_result_ids:
            logs.append('filtering')
            results = results.exclude(pk__in=cached_inference_result_ids)

        nodes = []
        edges = []
        processed_node_ids = set()
        processed_undirected_edges = set()
        for res in results:
            nodes, edges, processed_node_ids, processed_undirected_edges  = self.add(
                    res,
                    nodes,
                    edges,
                    processed_node_ids,
                    processed_undirected_edges,
                    )
            elements.extend(nodes)
            elements.extend(edges)
        return JsonResponse({"elements": elements})



class run(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """ Request comes in as a list of algorithms to run.
        """
        # Create study
        study = Study.objects.create(
                name = request.data['name'],
                description = request.data.get('description', None),
                status = 'RECIEVED',
                user = request.user,
                )
        study.save()
        # Build gennifer requests
        tasks = request.data['tasks']
        response = {"study_id": study.pk, "tasks": []}
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
            task["task_id"] = create_task.delay(algo.name, zenodo_id, hyperparameters, request.user.pk, study.pk).id
            response["tasks"].append(task)
        return JsonResponse(response)
