from django.contrib import admin

from .models import Algorithm, Dataset, InferenceStudy

admin.site.register(Algorithm)
admin.site.register(Dataset)
admin.site.register(InferenceStudy)
