import time
import logging
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from .models import Transaction
from .apps import ChpApiConfig

from chp.trapi_interface import TrapiInterface, parse_query_graph
import chp
import pybkb
import chp_data
import chp_client

# Setup logging
logging.addLevelName(25, "INFO2")
# Add a special logging function
def info2(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)
logging.Logger.info2 = info2
logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self, request):
        self.query, self.max_results, self.client_id = self._process_request(request)

    @staticmethod
    def _process_request(request):
        logger.info2('Starting query.')
        data = request.data
        query = data.pop('message', None)
        max_results = data.pop('max_results', 10)
        client_id = data.pop('client_id', 'default')
        return query, max_results, client_id

    def get_response_to_query(self):
        start_time = time.time()
        #logger.info('Database as {} entries.'.format(Transaction.objects.all().count()))

        # First check if query_graph is in cache
        query, cached_responses, query_map = self._get_response_from_cache(self.query)
        if cached_responses is not None:
            logger.info2('Found {} cached responses.'.format(len(cached_responses)))

        if query is not None:
            logger.info2('Running query.')
            # Instaniate TRAPI Interface
            interface = TrapiInterface(
                query=query,
                hosts_filename=ChpApiConfig.hosts_filename,
                num_processes_per_host=ChpApiConfig.num_processes_per_host,
                max_results=self.max_results,
                client_id=self.client_id,
                bkb_handler=ChpApiConfig.bkb_handler,
                joint_reasoner=ChpApiConfig.joint_reasoner,
                dynamic_reasoner=ChpApiConfig.dynamic_reasoner,
            )

            # Build queries
            interface.build_chp_queries()
            logger.info2('Built Queries.')
            # Run queries
            interface.run_chp_queries()
            logger.info2('Completed Reasoning in {} seconds.'.format(time.time() - start_time))

            # Construct Response
            response = interface.construct_trapi_response()
            logger.info2('Constructed TRAPI response.')

            # Put result in cache wrapped in a single SQL transaction
            with transaction.atomic():
                logger.info2('Putting results in cache.')
                if type(response) == list:
                    for _resp in response:
                        self._process_transaction(_resp)
                else:
                    self._process_transaction(response)
                logger.info2('Results saved in cache.')

        if cached_responses is not None:
            # Check for batch query
            if type(cached_responses) == list:
                logger.info2('Reordering batch query.')
                if query is not None:
                    response = self._reorder_response(response, cached_responses, query_map)
                else:
                    response = cached_responses
                response = self._wrap_batch_responses(response)
            else:
                response = cached_responses
        else:
            # Check if a batch query and wrap the response
            if type(response) == list:
                response = self._wrap_batch_responses(response)

        logger.info2('Responded in {} seconds'.format(time.time() - start_time))
        return JsonResponse(response)

    def _find_close_cached_query(self, parsed_query, potential_objs, threshold=None):
        """ This fuction will find a query that matches exactly genes, drugs, disease, outcome name,
            outcome operator, but will try to find a close query in the outcome value given by the threshold.

            :param query: The query.
            :type query: dict
            :param threshold: The fraction (distance from outcome value) / outcome_value. If this fraction is
                less than the threshold it will not return that query. Default None, in which no threshold of this fraction
                is acceptable so just return None.
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
        response = {"message": []}
        for resp in batch_response_list:
            response["message"].append(resp.pop("message"))
        return response

