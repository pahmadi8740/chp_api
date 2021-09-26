from django.db import models
# Create your models here.

class Transaction(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    date_time = models.DateTimeField(auto_now=True)
    query = models.JSONField(default=dict)
    status = models.CharField(max_length=100, default="", null=True)
    chp_version = models.CharField(max_length=100, default="")
    chp_data_version = models.CharField(max_length=100, default="")
    pybkb_version = models.CharField(max_length=100, default="")
    chp_client_version = models.CharField(max_length=100, default="")
    chp_utils_version = models.CharField(max_length=100, default="")

    class Meta:
        app_label = 'dispatcher'