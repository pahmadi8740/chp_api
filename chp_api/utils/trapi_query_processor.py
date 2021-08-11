import logging
from copy import deepcopy

#from django.db import transaction
#from django.http import JsonResponse
#from django.core.exceptions import ObjectDoesNotExist

#from trapi_model.query import Query
#from trapi_model.biolink.constants import *

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
        

''' Depreciate

    def _find_close_cached_query(self, parsed_query, potential_objs, threshold=None):
        """ This fuction will find a query that matches exactly genes, drugs, disease, outcome name,
            outcome operator, but will try to find a close query in the outcome value given by the threshold.

            :param query: The query.
            :type query: dict
            :param threshold: The fraction (distance from outcome value) / outcome_value. If this fraction is
                less than the threshold it will not return that query. Default None, in which no threshold of this fraction
                is acceptable so just return None.
            :type threshold: float
        """
        if threshold is None:
            return None
        # Find the closest object
        dist = None
        closest_obj = None
        for obj in potential_objs:
            if dist is None:
                _dist = abs(obj.outcome_value - parsed["outcome_value"])
                if (_dist / parsed["outcome_value"]) < threshold:
                    dist = _dist
                    closest_obj = obj
            else:
                _dist = abs(obj.outcome_value - parsed["outcome_value"])
                if (_dist / parsed["outcome_value"]) < threshold and _dist < dist:
                    dist = _dist
                    closest_obj = obj
        # Return the response of the closest object.
        logger.info('Found a close response.')
        return closest_obj.chp_response

    def _find_cached_query(self, query):
        """ Search the database to see if the query exists.
        """
        parsed = parse_query_graph(query["query_graph"])
        if parsed is None:
            return None
        potential_objs = Transaction.objects.filter(
            genes__exact=parsed["genes"],
            therapeutic__exact=parsed["therapeutic"],
            disease__exact=parsed["disease"],
            outcome_name__exact=parsed["outcome_name"],
            outcome_op__exact=parsed["outcome_op"],
        )
        if len(potential_objs) == 0:
            return None
        # Try to find an exact match
        try:
            exact_obj = potential_objs.get(query_graph=query["query_graph"])
            logger.info('Found an exact response.')
            return exact_obj.chp_response
        except ObjectDoesNotExist:
            logger.debug('Trying to find a close response.')
            return self._find_close_cached_query(parsed_query)

    def _get_response_from_cache(self, query):
        """ Parent function that starts the search for a response to a specific query.
        """
        # Testing 
        if type(query) == list:
            return query, None, {"query": [i for i in range(len(query))]}
        else:
            return query, None, None
        logger.info('Trying to find a suitable response in the cache.')
        # Detect if batch query
        if type(query) == list:
            new_query = []
            cached_responses = []
            query_map = {"query": [], "cached_responses": []}
            for idx, _query in enumerate(query):
                response = self._find_cached_query(_query)
                if response is None:
                    new_query.append(_query)
                    query_map["query"].append(idx)
                else:
                    cached_responses.append(response)
                    query_map["cached_response"].append(idx)
            return new_query, cached_responses, query_map
        else:
            response = self._find_cached_query(query)
            if response is None:
                return query, None, None
            else:
                return None, response, None

    def _process_transaction(self, response):
        """ Save the query response as a transaction in the database.
        """
        # Use the trapi interface function to get the chp client variables
        parsed = parse_query_graph(response["message"]["query_graph"])

        logger.info('Putting response in cache.')

        # Save the transaction
        _transaction = Transaction(
            query_graph = response["message"]["query_graph"],
            chp_response = response,
            chp_version = chp.__version__,
            chp_data_version = chp_data.__version__,
            pybkb_version = pybkb.__version__,
            chp_client_version = chp_client.__version__,
            genes = parsed["genes"],
            therapeutic = parsed["therapeutic"],
            disease = parsed["disease"],
            outcome_name = parsed["outcome_name"],
            outcome_op = parsed["outcome_op"],
            outcome_value = parsed["outcome_value"] if not parsed["outcome_value"] == '' else 0,
        )
        _transaction.save()

    def _reorder_response(self, response, cached_responses, query_map):
        """ Orders the response so that queries found in the database are correctly
            combined with queries that had to be calculated in real-time.
        """
        unordered_response = []
        for key, indices in query_map.items():
            if key == 'query':
                for idx, resp in zip(indices, response):
                    unordered_response.append((idx, resp))
            elif key == 'cached_response':
                for idx, resp in zip(indices, cached_responses):
                    unordered_response.append((idx, resp))
        ordered_response = [resp for _, resp in sorted(unordered_response)]
        return ordered_response

    def _wrap_batch_responses(self, batch_response_list):
        """ Wraps batch response inside a message key.
        """
        response = {"message": []}
        for resp in batch_response_list:
            response["message"].append(resp.pop("message"))
        return response

    def _build_error_response(self, error_msg):
        """ Builds a stock message back in the event a 400 level error has occured.
        """

        response = { 'query_graph' : { 'edges': dict(), 'nodes': dict()},
                     'knowledge_graph' : { 'edges': dict(), 'nodes': dict()},
                     'results': [] }
        message = {'message' : response,
                   'description' : 'Unsupported query',
                   'status': 'Bad Request. ' + error_msg}
        return message
'''
