from django.db import models
# Create your models here.

class Transaction(models.Model):
    date_time = models.DateTimeField(auto_now=True)
    source_ara = models.CharField(max_length=50)

    query = models.JSONField()
    response = models.JSONField()
    
    english_translation = models.TextField()