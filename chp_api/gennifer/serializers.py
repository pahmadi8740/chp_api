from rest_framework import serializers

from .models import Dataset, Study, Task, Result, Algorithm, Gene, UserAnalysisSession


class UserAnalysisSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnalysisSession
        fields = ['id', 'user', 'name', 'session_data', 'is_saved']

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['title', 'zenodo_id', 'doi', 'description']
        read_only_fields = ['title', 'doi', 'description']

class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = ['name', 'status', 'description', 'timestamp', 'user']


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
            'max_study_edge_weight', 
            'min_study_edge_weight', 
            'avg_study_edge_weight', 
            'std_study_edge_weight',
            'name',
            'study',
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
