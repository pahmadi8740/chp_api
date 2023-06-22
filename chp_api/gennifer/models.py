import requests
import uuid

from django.db import models
from django.contrib.auth.models import User


class UserAnalysisSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_data = models.JSONField()
    is_saved = models.BooleanField(default=False)

    def update_session_data(self, new_data):
        self.session_data.update(new_data)
        self.save()

    def __str__(self):
        return self.name

class Algorithm(models.Model):
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    edge_weight_description = models.TextField(null=True, blank=True)
    edge_weight_type = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    directed = models.BooleanField()

    def __str__(self):
        return self.name


class AlgorithmInstance(models.Model):
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE, related_name='instances')
    hyperparameters = models.JSONField(null=True)

    def __str__(self):
        if self.hyperparameters:
            hypers = tuple([f'{k}={v}' for k, v in self.hyperparameters.items()])
        else:
            hypers = '()'
        return f'{self.algorithm.name}{hypers}'


class Dataset(models.Model):
    title = models.CharField(max_length=128)
    zenodo_id = models.CharField(max_length=128, primary_key=True)
    doi = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    upload_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        import re
        
        CLEANR = re.compile('<.*?>')

        info = self.get_record()
        if 'status' in info and 'message' in info and len(info) == 2:
            # This means that retrieval failed
            raise ValueError(f'Could not retrieve zenodo record {self.zenodo_id}. Failed with message: {info["message"]}')
        self.doi = info["doi"]
        self.description = re.sub(CLEANR, '', info["metadata"]["description"])
        self.title = re.sub(CLEANR, '', info["metadata"]["title"])

        super(Dataset, self).save(*args, **kwargs)

    def get_record(self):
        return requests.get(f"https://zenodo.org/api/records/{self.zenodo_id}").json()

    def __str__(self):
        return f'zenodo:{self.zenodo_id}'

class Gene(models.Model):
    name = models.CharField(max_length=128)
    curie = models.CharField(max_length=128)
    variant = models.TextField(null=True, blank=True)
    chp_preferred_curie = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name


class InferenceStudy(models.Model):
    algorithm_instance = models.ForeignKey(AlgorithmInstance, on_delete=models.CASCADE, related_name='studies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='studies')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='studies')
    timestamp = models.DateTimeField(auto_now_add=True)
    # Study characteristics for all edge weights in a given study over a dataset
    max_study_edge_weight = models.FloatField(null=True)
    min_study_edge_weight = models.FloatField(null=True)
    avg_study_edge_weight = models.FloatField(null=True)
    std_study_edge_weight = models.FloatField(null=True)
    is_public = models.BooleanField(default=False)
    status = models.CharField(max_length=10)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.algorithm_instance} on {self.dataset.zenodo_id}'


class InferenceResult(models.Model):
    # Stands for transcription factor
    tf = models.ForeignKey(Gene, on_delete=models.CASCADE, related_name='inference_result_tf')
    # Target is the gene that is regulated by the transcription factor
    target = models.ForeignKey(Gene, on_delete=models.CASCADE, related_name='inference_result_target')
    edge_weight = models.FloatField()
    study = models.ForeignKey(InferenceStudy, on_delete=models.CASCADE, related_name='results')
    is_public = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='results')

    def __str__(self):
        return f'{self.tf}:{self.tf.curie} -> regulates -> {self.target}:{self.target.curie}'
