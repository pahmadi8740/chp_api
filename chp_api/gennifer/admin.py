from django.contrib import admin

from .models import Algorithm, Dataset, Study, Task, Result, Gene, UserAnalysisSession

admin.site.register(Algorithm)
admin.site.register(Dataset)
admin.site.register(Study)
admin.site.register(Task)
admin.site.register(Result)
admin.site.register(Gene)
admin.site.register(UserAnalysisSession)
