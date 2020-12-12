from django.db import models
# Create your models here.

class Transaction(models.Model):
    date_time = models.DateTimeField(auto_now=True)
    query_graph = models.JSONField(default=dict)
    chp_response = models.JSONField(default=dict)
    chp_version = models.CharField(max_length=100, default="")
    chp_data_version = models.CharField(max_length=100, default="")
    pybkb_version = models.CharField(max_length=100, default="")
    chp_client_version = models.CharField(max_length=100, default="")
    genes = models.JSONField(default=dict)
    therapeutic = models.CharField(max_length=100, default="")
    disease = models.CharField(max_length=100, default="")
    outcome_name = models.CharField(max_length=100, default="")
    outcome_op = models.CharField(max_length=10, default="")
    outcome_value = models.IntegerField(default=0)
