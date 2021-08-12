from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
        host(r'www', settings.ROOT_URLCONF, name='www'),
        host(r'(breast|brain|lung)', 'apis.chp_core.urls', name='chp-core'),
        )
