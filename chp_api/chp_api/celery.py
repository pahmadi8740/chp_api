import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chp_api.settings")
app = Celery(
        "chp_api",
        include=['gennifer.tasks'],
        )
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.update({
    "task_routes": {
        "create_gennifer_task": {"queue": 'chp_api'}
        }
    })
