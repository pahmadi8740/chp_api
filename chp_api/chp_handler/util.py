import time
import logging
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from .models import Transaction
from .apps import ChpApiConfig, ChpBreastApiConfig, ChpBrainApiConfig, ChpLungApiConfig

from trapi_model.query import Query
from trapi_model.biolink.constants import *

from chp.trapi_interface import TrapiInterface, parse_query_graph
import chp
import pybkb
import chp_data
import chp_client
import requests
import json
from copy import deepcopy

# Setup logging
logging.addLevelName(25, "NOTE")
# Add a special logging function
def note(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)
logging.Logger.note = note
logger = logging.getLogger(__name__)

class QueryProcessor:
    """ Query Processor class used to abstract the processing infrastructure from
        the views:

        :param request: Incoming POST request with a TRAPI message.
        :type request: request
    """
    def __init__(self, request, trapi_version):
        #self.process_subclasses(request, trapi_version=trapi_version)
        self.query, self.chp_config = self._process_request(request, trapi_version=trapi_version)
        self.query_copy = self.query.get_copy()
        self.trapi_version = trapi_version
        self.original_query_graph = request.data['message']['query_graph']

    @staticmethod
    def _process_request(request, trapi_version='1.1'):

        def _biolink_category_descendent_lookup(biolinkCategory):
            url = "https://bl-lookup-sri.renci.org/bl/"+biolinkCategory+"/descendants?version=latest"
            response = requests.get(url)
            return response.json()
        
        def _process_subclasses(data, trapi_version='1.1'):
            query = Query.load(trapi_version, biolink_version=None, query=data)
            #get nodes
            drug_nodes_found = False
            gene_nodes_found = False
            nodes = query.message.query_graph.nodes
            for node in nodes:
                node_obj = nodes[node]
                curies = node_obj.ids

                passed_categories = []
                categories = node_obj.categories             

                if curies is not None:
                    for curie in curies:
                        if "MONDO" in curie:
                            #check if we support the specificied categories
                            #if we do not support the specified categories, see if we can support descendants 
                            logger.note('what the fuck')
                            if get_biolink_entity("biolink:Disease") not in node_obj.categories:
                                for category in node_obj.categories:
                                    descendants = _biolink_category_descendent_lookup(category.passed_name)
                                    if "biolink:Disease" in descendants:
                                        node_obj.set_categories("biolink:Disease")
                        elif "ENSEMBL" in curie:
                            logger.note('im tired')
                            gene_nodes_found = True
                            if get_biolink_entity("biolink:Gene") not in node_obj.categories:
                                for category in node_obj.categories:
                                    descendants = _biolink_category_descendent_lookup(category.passed_name)
                                    if "biolink:Gene" in descendants:
                                        node_obj.set_categories("biolink:Gene")
                        elif "CHEMBL" in curie:
                            logger.note('blah')
                            drug_nodes_found = True
                            if get_biolink_entity("biolink:Drug") not in node_obj.categories:
                                for category in node_obj.categories:
                                    descendants = _biolink_category_descendent_lookup(category.passed_name)
                                    if "biolink:Drug" in descendants:
                                        node_obj.set_categories("biolink:Drug")
                        elif "EFO" in curie:
                            logger.note('suh')
                            if get_biolink_entity("biolink:PhenotypicFeature") not in node_obj.categories:
                                for category in node_obj.categories:
                                    descendants = _biolink_category_descendent_lookup(category.passed_name)
                                    if "biolink:PhenotypicFeature" in descendants:
                                        node_obj.set_categories("biolink:PhenotypicFeature")
                query.message.query_graph.nodes[node] = node_obj

            #get edges
            edges = query.message.query_graph.edges              
            for edge in edges:
                edge_obj = edges[edge]
                if nodes[edge_obj.subject].ids is not None and nodes[edge_obj.object].ids is not None:  
                    for subject_id in nodes[edge_obj.subject].ids:
                        for object_id in nodes[edge_obj.object].ids:
                            if "ENSEMBL" in subject_id:
                                if "CHEMBL" in object_id:
                                    if get_biolink_entity("biolink:interacts_with") not in edge_obj.predicates:
                                        for predicate in edge_obj.predicates:
                                            descendants = _biolink_category_descendent_lookup(predicate.passed_name)
                                            if "biolink:interacts_with" in descendants:
                                                edge_obj.set_predicates("biolink:interacts_with")
                                if "MONDO" in object_id:
                                    if get_biolink_entity("biolink:gene_associated_with_condition") not in edge_obj.predicates:
                                        for predicate in edge_obj.predicates:
                                            descendants = _biolink_category_descendent_lookup(predicate.passed_name)
                                            if "biolink:gene_associated_with_condition" in descendants:
                                                edge_obj.set_predicates("biolink:gene_associated_with_condition")
                            if "CHEMBL" in subject_id:
                                if "MONDO" in object_id:
                                    if get_biolink_entity("biolink:treats") not in edge_obj.predicates:
                                        for predicate in edge_obj.predicates:
                                            descendants = _biolink_category_descendent_lookup(predicate.passed_name)
                                            if "biolink:treats" in descendants:
                                                edge_obj.set_predicates("biolink:treats")
                                if "ENSEMBL" in object_id:
                                    if get_biolink_entity("biolink:interacts_with") not in edge_obj.predicates:
                                        for predicate in edge_obj.predicates:
                                            descendants = _biolink_category_descendent_lookup(predicate.passed_name)
                                            if "biolink:interacts_with" in descendants:
                                                edge_obj.set_predicates("biolink:interacts_with")
                            if "MONDO" in subject_id:
                                if "EFO" in object_id:
                                    if get_biolink_entity("biolink:has_phenotype") not in edge_obj.predicates:
                                        for predicate in edge_obj.predicates:
                                            descendants = _biolink_category_descendent_lookup(predicate.passed_name)
                                            if "biolink:has_phenotype" in descendants:
                                                edge_obj.set_predicates("biolink:has_phenotype")
                            query.message.query_graph.edges[edge] = edge_obj

            data = query.to_dict()
            #handle wildcard queries
            #drugwildcard with genes specified
            if drug_nodes_found and not gene_nodes_found:
                for node in nodes:
                    node_obj = nodes[node]
                    if node_obj.ids is None:
                        for category in node_obj.categories:
                            descendants = _biolink_category_descendent_lookup(category.passed_name)
                            if "biolink:Gene" in descendants:
                                node_obj.set_categories("biolink:Gene")
                                query.message.query_graph.nodes[node] = node_obj
                data = query.to_dict()
            #genewildcard with drugs specified
            elif gene_nodes_found and not drug_nodes_found:
                for node in nodes:
                    node_obj = nodes[node]
                    if node_obj.ids is None:
                        for category in node_obj.categories:
                            descendants = _biolink_category_descendent_lookup(category.passed_name)
                            if "biolink:Drug" in descendants:
                                node_obj.set_categories("biolink:Drug")
                                query.message.query_graph.nodes[node] = node_obj
                data = query.to_dict()
            elif not gene_nodes_found and not drug_nodes_found:
                for node in nodes:
                    node_obj = nodes[node]
                    if node_obj.ids == None:    
                        #find edge for this node
                        for edge in edges:
                            edge_obj = edges[edge]
                            if edge_obj.subject == node:
                                #check constraints for context
                                drug_constraint = edge_obj.find_constraint("drug")
                                gene_constraint = edge_obj.find_constraint("gene")
                                #gene wildcard by drug found in constraint
                                if drug_constraint is not None:
                                    node_obj.set_categories("biolink:Gene")
                                    query.message.query_graph.nodes[node] = node_obj
                                    if nodes[edge_obj.object].category == "biolink:Gene":
                                        edge_obj.set_predicates("biolink:interacts_with")
                                        query.message.query_graph.edges[edge] = edge_obj
                                    elif nodes[edge_obj.object].category == "biolink:Disease":
                                        edge_obj.set_predicates("biolink:gene_associated_with_condition")
                                        query.message.query_graph.edges[edge] = edge_obj
                                    data = query.to_dict()
                                #drug wildcard by gene found in constraint
                                elif gene_constraint is not None:
                                    node_obj.set_categories("biolink:Drug")
                                    query.message.query_graph.nodes[node] = node_obj
                                    if nodes[edge_obj.object].category == "biolink:Gene":
                                        edge_obj.set_predicates("biolink:interacts_with")
                                        query.message.query_graph.edges[edge] = edge_obj
                                    elif nodes[edge_obj.object].category == "biolink:Disease":
                                        edge_obj.set_predicates("biolink:treats")
                                        query.message.query_graph.edges[edge] = edge_obj
                                    data = query.to_dict()
                                else:
                                    #create batch queries because not enough context found
                                    #create copy of query
                                    #query.message.query_graph.nodes[node].set_categories(["biolink:Gene","biolink:Drug"])
                                    #query.message.query_graph.edges[edge].set_predicates(["biolink:gene_associated_with_condition","biolink:treats"])
                                    #data = query.to_dict()
                                    continue
                            continue
            return data

        """ Helper function that extracts the query from the message.
        """
        logger.note('Starting query.')
        data = request.data
        data = _process_subclasses(data, trapi_version=trapi_version)
        host = request.headers['Host']
        # Parse host name
        host_parse = host.split('.')
        # API subdomain is the ChpConfig to use.
        api = host_parse[0]
        logger.note(data)
        query = Query.load(trapi_version, None, query=data)
        disease_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_DISEASE_ENTITY])
        if 'breast' in api:
            chp_config = ChpBreastApiConfig
        elif 'brain' in api:
            chp_config = ChpBrainApiConfig
        elif 'lung' in api:
            chp_config = ChpLungApiConfig
        elif disease_nodes_ids is not None:
            if len(disease_nodes_ids) > 1:
                chp_config = ChpApiConfig
            disease_node = query.message.query_graph.nodes[disease_nodes_ids[0]]
            if disease_node.ids[0] == 'MONDO:0005061':
                chp_config = ChpLungApiConfig
            elif disease_node.ids[0] == 'MONDO:0001657':
                chp_config = ChpBrainApiConfig
            elif disease_node.ids[0] == 'MONDO:0007254':
                chp_config = ChpBreastApiConfig
            else:
                chp_config = ChpApiConfig
        else:
            chp_config = ChpApiConfig
        #query = data.pop('message', None)
        #max_results = data.pop('max_results', 10)
        #client_id = data.pop('client_id', 'default')
        #return query, max_results, client_id
        return query, chp_config

    def get_response_to_query(self):
        """ Main function of the processor that handles primary logic for obtaining
            a cached or calculated query response.
        """
        #logger.info('Database as {} entries.'.format(Transaction.objects.all().count()))

        # First check if query_graph is in cache
        #query, cached_responses, query_map = self._get_response_from_cache(self.query)
        #if cached_responses is not None:
        #    logger.note('Found {} cached responses.'.format(len(cached_responses)))

        start_time = time.time()
        if self.query is not None:
            logger.note('Running query.')
            try:
            # Instaniate TRAPI Interface
                interface = TrapiInterface(
                    query=self.query,
                    hosts_filename=self.chp_config.hosts_filename,
                    num_processes_per_host=self.chp_config.num_processes_per_host,
                    bkb_handler=self.chp_config.bkb_handler,
                    joint_reasoner=self.chp_config.joint_reasoner,
                    dynamic_reasoner=self.chp_config.dynamic_reasoner,
                )

                # Build queries
                interface.build_chp_queries()
            except Exception as e:
                query_dict = self.query_copy.to_dict()
                query_dict['status'] = 'Bad request.' + str(e)
                return JsonResponse(query_dict)



            logger.note('Built Queries.')
            # Run queries
            try:
                reasoning_start_time = time.time()
                interface.run_chp_queries()
                logger.note('Completed Reasoning in {} seconds.'.format(time.time() - reasoning_start_time))
            except Exception as e:
                logger.critical('Error during reasoning.')
                query_dict = self.query_copy.to_dict()
                query_dict['status'] = 'Unexpected error.' + str(e)
                return JsonResponse(query_dict)

            # Construct Response
            response = interface.construct_trapi_response()
            logger.note('Constructed TRAPI response.')

            '''
            # Put result in cache wrapped in a single SQL transaction
            with transaction.atomic():
                logger.note('Putting results in cache.')
                if type(response) == list:
                    for _resp in response:
                        self._prosdfcess_transaction(_resp)
                else:
                    self._process_transaction(response)
                logger.note('Results saved in cache.')
            '''
        '''
        if cached_responses is not None:
            # Check for batch query
            if type(cached_responses) == list:
                logger.note('Reordering batch query.')
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
        '''
        logger.note('Responded in {} seconds'.format(time.time() - start_time))
        response_dict = response.to_dict()
        response_dict['message']['query_graph']=self.original_query_graph
        response_dict['status'] = 'Success'
        return JsonResponse(response_dict)

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

        response = { 'query_graph' : self.query,
                     'knowledge_graph' : { 'edges': dict(), nodes: dict()},
                     'results': [] }
        message = {'message' : response,
                   'description' : 'Unsupported query',
                   'status': 'Bad Request. ' + error_msg}
        return message


