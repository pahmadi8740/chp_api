from rest_framework import serializers

from .models import Dataset, InferenceStudy, InferenceResult, Algorithm, Gene, UserAnalysisSession


class UserAnalysisSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnalysisSession
        fields = ['id', 'user', 'name', 'session_data', 'is_saved']

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['title', 'zenodo_id', 'doi', 'description']
        read_only_fields = ['title', 'doi', 'description']


class InferenceStudySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')

    def get_name(self, study):
        return f'{study.algorithm_instance.algorithm.name} on {study.dataset.title}'

    class Meta:
        model = InferenceStudy
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
            'status',
            ]

class InferenceResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceResult
        fields = [
            'pk',
            'tf',
            'target',
            'edge_weight',
            'study',
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
