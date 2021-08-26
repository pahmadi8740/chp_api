import logging
from copy import deepcopy
from django.http import JsonResponse

from chp_utils.trapi_query_processor import BaseQueryProcessor

from utils.mixins.chp_core_query_processor_mixin import ChpCoreQueryProcessorMixin

# Setup logging
logging.addLevelName(25, "NOTE")
# Add a special logging function
def note(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)
logging.Logger.note = note
logger = logging.getLogger(__name__)


class ApiBaseProcessor(BaseQueryProcessor):
    def __init__(self, request, trapi_version):
        """ Base API Query Processor class used to abstract the processing infrastructure from
            the views. Inherits from the CHP Utilities Trapi Query Processor which handles
            node normalization, curie ontology expansion, and semantic operations.

            :param request: Incoming POST request with a TRAPI message.
            :type request: requests.request
        """
        self.request_data = deepcopy(request.data)
        self.chp_config, self.passed_subdomain = self.get_app_config(request)
        self.trapi_version = trapi_version      
        super().__init__(None)

    def process_invalid_trapi(self, request):
        invalid_query_json = request.data
        invalid_query_json['status'] = 'Bad TRAPI.'
        return JsonResponse(invalid_query_json, status=400)

    @staticmethod
    def get_app_config(request):
       pass

    def process_request(self, request, trapi_version):
        pass

    def get_response(self, query):
        pass

    def add_transactions(self, responses):
        for response in responses:
            self.add_transaction(response)
    
    def add_transaction(self, response):
        pass


class ChpCoreQueryProcessor(ChpCoreQueryProcessorMixin, ApiBaseProcessor):
    pass
        
