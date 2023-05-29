from django.db import models
from django.contrib.auth.models import User


class Algorithm(models.Model):
    name = models.CharField(max_length=128)
    run_url = models.URLField(max_length=128)

    def __str__(self):
        return self.name


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
        self.doi = info["doi"]
        self.description = re.sub(CLEANR, '', infoi["metadata"]["description"])
        self.title = re.sub(CLEANR, '', infoi["metadata"]["title"])

    def get_record(self):
        return requests.get(f"https://zenodo.org/api/records/{self.zenodo_id}").json()


class Gene(models.Model):
    name = models.CharField(max_length=128)
    curie = models.CharField(max_length=128)
    variant = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class InferenceStudy(models.Model):
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE, related_name='studies')
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

class InferenceResult(models.Model):
    # Stands for transcription factor
    tf = models.ForeignKey(Gene, on_delete=models.CASCADE)
    # Target is the gene that is regulated by the transcription factor
    target = models.ForeignKey(Gene, on_delete=models.CASCADE)
    edge_weight = models.FloatField()
    study = models.ForeignKey(InferenceStudy, on_delete=models.CASCADE, related_name='results')
    is_public = models.BooleanField(default=False)
