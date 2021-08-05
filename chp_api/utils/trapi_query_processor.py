import logging
from copy import deepcopy

from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from trapi_model.query import Query
from trapi_model.biolink.constants import *
from chp_utils.client import SriNodeNormalizerApiClient, SriOntologyKpApiClient

from chp_utils.trapi_query_processor import BaseQueryProcessor

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
        self.data_copy = deepcopy(request.data)
        self.request_process_failure_response = None
        self.query, self.chp_config = self._process_request(request, trapi_version=trapi_version)
        self.trapi_version = trapi_version      
        super().__init__(Query.load(trapi_version, None, query=request.data))

    @staticmethod
    def _process_request(request, trapi_version):
        pass

class ChpCoreQueryProcessor(ChpCoreQueryProcessorMixin, ApiBaseProcessor):
    pass
        


class BaseQueryProcessor:
    def __init__(self, request, trapi_version):
    
    def _process_request(request, trapi_version):
        pass

    def fill_biolink_categories(self, query):
        return query

    def _extract_all_curies(self, query):
        curies = []
        query_graph = query.message.query_graph
        for node_id, node in query_graph.items():
            if node.ids is not None:
                curies.extend(node.ids)
        return curies

    def _get_most_general_preference(self, possible_preferences):
        unsorted_entities = []
        for curie, category in possible_preferences:
            unsorted_entities.append((len(category.get_ancestors()), curie, category))
        return sorted(unsorted_entities)[0]

    def _get_preferred(self, query, curie, categories, normalization_dict, meta_knowledge_graph):
        # Ensure query graph categories and normalization type (categories) are consistent
        curie_types = normalization_dict[curie]["types"]
        curie_prefix = curie.split(':')[0]
        possible_preferences = []
        for curie_type in curie_types:
            if curie_type in meta_knowledge_graph.nodes:
                preferred_prefix = meta_knowledge_graph[curie_type]
                if curie_prefix != preferred_prefix:
                    for equivalent_id in normalization_dict[curie]['equivalent_identifers']:
                        equiv_prefix = equivalent_id.split(':')[0]
                        if equiv_prefix == preferred_prefix:
                            possible_preferences.append(
                                    (equivalent_id, curie_type)
                                    )
                            break
                else:
                    possible_preferences.append(
                            (curie, curie_type)
                            )
        # Go through each possible preference and return the preferred curie that with the most general category
        if len(possible_preferences) == 0:
            query.warning('Could not normalize curie: {}, probably will cause failure.'.format(curie))
            return curie, categories
        if len(possible_preferences) > 1:
            preferred_curie, preferred_category = self._get_most_general_preference(possible_preferences)
        else:
            preferred_curie, preferred_category = possible_preferences[0]
        return preferred_curie, preferred_category

    def _normalize_query_graphs(self, queries, normalization_dict, meta_knowledge_graph):
        normalization_map = {}
        for query in queries:
            query_graph = query.message.query_graph
            for node_id, node in query_graph.items():
                if node.ids is None:
                    continue
                # Get preferred curie and category based on meta kg
                preferred_curie, preferred_category = self._get_preferred(
                        query,
                        node.ids[0],
                        node.categories[0],
                        normalization_dict, 
                        meta_knowledge_graph,
                        )
                # Check if curie was actually converted
                if curie != preferred_curie:
                    normalization_map[preferred_curie] = curie
                    node.ids = [preferred_curie]
                # Check categories alignment
                if node.categories is None:
                    node.categories = [preferred_category]
                    query.info(
                            'Filling in empty category for node {}, with {}'.format(
                                node_id,
                                preferred_category,
                                )
                            )
                elif node.categories[0] != preferred_category:
                    node.categories = [preferred_category]
                    query.warning(
                        'Passed category for node: {}, did not match our \
                            preferred category {} for this curie. Going with our preferred category.'.format(
                                node_id,
                                preferred_category,
                                )
                            )
        return queries, normalization_map

    def normalize_to_preferred(self, queries, meta_knowledge_graph):
        # Instantiate client
        node_normalizer_client = SriNodeNormalizerApiClient()
        
        # Get all curies to normalize
        curies_to_normalize = self._extract_all_curies(queries)

        # Get normalized nodes
        normalization_dict = node_normalizer_client.get_normalized_nodes(curies_to_normalize)

        # Normalize query graph
        return self._normalize_query_graphs(queries, normalization_dict, meta_knowledge_graph)
    
    def expand_batch_query(self, query):
        # Expand if batch query
        if query.is_batch_query():
            return query.expand_batch_query()
        # Otherwise wrap query in list
        return [query]

    def expand_supported_ontological_descendents(self, queries):
        #TODO: For each query in queries expand that single query to cover all supported ontology classes,
        # append them to a set of new queries, don't append the more general one only supported descendents.
        return queries

    def expand_with_semantic_ops(self, queries):
        return queries

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

class ChpCoreQueryProcessor(ChpCoreQueryProcessorMixin, BaseQueryProcessor):
    pass
