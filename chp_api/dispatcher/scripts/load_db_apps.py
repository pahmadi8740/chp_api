from django.conf import settings

from ..models import App


def run():
    for app_name in settings.INSTALLED_CHP_APPS:
        app_db_obj, created = App.objects.get_or_create(name=app_name)
        if created:
            app_db_obj.save()
