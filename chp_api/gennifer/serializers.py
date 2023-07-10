from rest_framework import serializers

from .models import (
        Dataset,
        Study,
        Task,
        Result,
        Algorithm,
        Gene,
        UserAnalysisSession,
        AlgorithmInstance,
        Hyperparameter,
        HyperparameterInstance,
        )


class UserAnalysisSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnalysisSession
        fields = ['id', 'user', 'name', 'session_data', 'is_saved']

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['pk', 'title', 'zenodo_id', 'doi', 'description']
        read_only_fields = ['pk', 'title', 'doi', 'description']

class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ['pk', 'name', 'status', 'description', 'timestamp', 'user', 'tasks']
        read_only_fields = ['pk', 'status']


class TaskSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')

    def get_name(self, study):
        return f'{study.algorithm_instance.algorithm.name} on {study.dataset.title}'

    class Meta:
        model = Task
        fields = [
            'pk',
            'algorithm_instance',
            'dataset', 
            'timestamp', 
            'max_task_edge_weight', 
            'min_task_edge_weight', 
            'avg_task_edge_weight', 
            'std_task_edge_weight',
            'name',
            'study',
            'status',
            ]
        read_only_fields = [
                'pk',
                'max_task_edge_weight', 
                'min_task_edge_weight', 
                'avg_task_edge_weight', 
                'std_task_edge_weight', 
                'name',
                'status',
                ]

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = [
            'pk',
            'tf',
            'target',
            'edge_weight',
            'task',
            ]

class AlgorithmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Algorithm
        fields = [
                'pk',
                'name',
                'description',
                'edge_weight_type',
                'directed',
                ]

class AlgorithmInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlgorithmInstance
        fields = [
                'pk',
                'algorithm',
                ]
        read_only_fields = ['pk']

    def create(self, validated_data):
        instance, _ = AlgorithmInstance.objects.get_or_create(**validated_data)
        return instance
        
class HyperparameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hyperparameter
        fields = [
                'pk',
                'name',
                'algorithm',
                'type',
                ]
        read_only_fields = ['pk', 'name', 'algorithm', 'type']

class HyperparameterInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HyperparameterInstance
        fields = [
                'pk',
                'algorithm_instance',
                'value_str',
                'hyperparameter',
                ]
        read_only_fields = ['pk']

    def create(self, validated_data):
        instance, _ = HyperparameterInstance.objects.get_or_create(**validated_data)
        return instance

class GeneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gene
        fields = [
                'pk',
                'name',
                'curie',
                'variant',
                'chp_preferred_curie',
                ]
