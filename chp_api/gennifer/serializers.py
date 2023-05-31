from rest_framework import serializers

from .models import Dataset, InferenceStudy, InferenceResult

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['upload_user', 'title', 'zenodo_id', 'doi', 'description']


class InferenceStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceStudy
        fields = [
            'algorithm_instance',
            'user', 
            'dataset', 
            'timestamp', 
            'max_study_edge_weight', 
            'min_study_edge_weight', 
            'avg_study_edge_weight', 
            'std_study_edge_weight', 
            'is_public',
            ]

class InferenceResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceResult
        fields = [
            'tf',
            'target',
            'edge_weight',
            'study',
            'is_public',
            'user',
            ]
