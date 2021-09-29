from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class GeneToPathway():
    gene = models.CharField(max_length=35, primary_key=True)
    pathways = ArrayField(models.JSONField())

    def get_result(self) -> list:
        return self.pathways

class PathwayToGene(models.Model):
    pathway = models.CharField(max_length=35, primary_key=True)
    genes = ArrayField(models.JSONField())

    def get_result(self) -> list:
        return self.genes

class CurieToCommonName(models.Model):
    curie = models.CharField(max_length=35, primary_key=True)
    commonName = ArrayField(models.CharField(max_length=100))

class Transaction(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    date_time = models.DateTimeField(auto_now=True)
    query = models.JSONField(default=dict)
    status = models.CharField(max_length=100, default="", null=True)
    chp_data_version = models.CharField(max_length=100, default="")
    chp_client_version = models.CharField(max_length=100, default="")
    chp_utils_version = models.CharField(max_length=100, default="")
    lookup_service_version = models.CharField(max_length=100, default="")