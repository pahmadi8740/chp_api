from django.http.response import JsonResponse
from rest_framework.views import APIView
from django.http import JsonResponse

class curies(APIView):
    trapi_version = '1.2'
    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(curies, self).__init__(**kwargs)
    
    def get(self, request):
        if request.method == 'GET':
            return JsonResponse({"foo":"goo"})