from django.db import models

class Transaction(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    date_time = models.DateTimeField(auto_now=True)
    query = models.JSONField(default=dict)
    status = models.CharField(max_length=100, default="", null=True)
    versions = models.JSONField(default=dict)
    chp_app = models.ForeignKey(App, on_delete=models.CASCADE)

class App(models.Model):
    name = models.CharField(max_length=128)
    curies_file = models.FileField(upload_to='curies_files/', null=True, blank=True)
    meta_knowledge_graph_file = models.FileField(upload_to='meta_knowledge_graph_files', null=True, blank=True)

    def __str__(self):
        return self.name


