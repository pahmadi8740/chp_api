import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chp_api.settings")
app = Celery("chp_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
