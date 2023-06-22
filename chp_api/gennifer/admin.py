from django.contrib import admin

from .models import Algorithm, Dataset, InferenceStudy, InferenceResult, Gene, UserAnalysisSession

admin.site.register(Algorithm)
admin.site.register(Dataset)
admin.site.register(InferenceStudy)
admin.site.register(InferenceResult)
admin.site.register(Gene)
admin.site.register(UserAnalysisSession)
