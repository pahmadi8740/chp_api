from django.db import models

class Transaction(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    date_time = models.DateTimeField(auto_now=True)
    query = models.JSONField(default=dict)
    status = models.CharField(max_length=100, default="", null=True)
    versions = models.JSONField(default=dict)
    chp_app = models.CharField(max_length=128, null=True)

