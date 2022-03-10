import logging
import time
from copy import deepcopy
from re import A
from django.http import JsonResponse
from django.apps import apps
from django.conf import settings
from importlib import import_module
from collections import defaultdict

from chp_utils.trapi_query_processor import BaseQueryProcessor
from chp_utils.curie_database import merge_curies_databases
from trapi_model.meta_knowledge_graph import merge_meta_knowledge_graphs
from trapi_model.query import Query
from trapi_model.biolink import TOOLKIT

from .models import Transaction

# Setup logging
logging.addLevelName(25, "NOTE")
# Add a special logging function
def note(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)
logging.Logger.note = note
logger = logging.getLogger(__name__)

# Installed CHP Apps
#CHP_APPS = [
#        "chp.app",
#        "chp_look_up.app",
#        ]

# Import CHP Apps
APPS = [import_module(app+'.app_interface') for app in settings.INSTALLED_CHP_APPS]

class Dispatcher(BaseQueryProcessor):
    def __init__(self, request, trapi_version):
        """ Base API Query Processor class used to abstract the processing infrastructure from
            the views. Inherits from the CHP Utilities Trapi Query Processor which handles
            node normalization, curie ontology expansion, and semantic operations.

            :param request: Incoming POST request with a TRAPI message.
            :type request: requests.request
        """
        self.request_data = deepcopy(request.data)

        #self.chp_config, self.passed_subdomain = self.get_app_config(request)
        self.trapi_version = trapi_version
        super().__init__(None)

    def get_curies(self):        
        curies_dbs = []
        for app in APPS:
            get_app_curies_fn = getattr(app, 'get_curies')
            curies_dbs.append(get_app_curies_fn())
        return merge_curies_databases(curies_dbs)

    def get_meta_knowledge_graph(self):
        meta_kgs = []
        for app in APPS:
            get_app_meta_kg_fn = getattr(app, 'get_meta_knowledge_graph')
            meta_kgs.append(get_app_meta_kg_fn())
        return merge_meta_knowledge_graphs(meta_kgs)

    def process_invalid_trapi(self, request):
        invalid_query_json = request.data
        invalid_query_json['status'] = 'Bad TRAPI.'
        return JsonResponse(invalid_query_json, status=400)

    def process_invalid_workflow(self, request, status_msg):
        invalid_query_json = request.data
        invalid_query_json['status'] = status_msg
        return JsonResponse(invalid_query_json, status=400)

    def process_request(self, request, trapi_version):
        """ Helper function that extracts the query from the message.
        """
        logger.info('Starting query.')
        query = Query.load(
                self.trapi_version,
                biolink_version=None,
                query=request.data
                )

        # Setup query in Base Processor
        self.setup_query(query)

        logger.info('Query loaded')
        
        return query

    def get_app_configs(self, query):
        """ Should get a base app configuration for your app or nothing.
        """
        app_configs = []
        for app in APPS:
            get_app_config_fn = getattr(app, 'get_app_config')
            app_configs.append(get_app_config_fn(query))
        return app_configs
    
    def get_trapi_interfaces(self, app_configs):
        """ Should load a base interface of your app.
        """
        if len(app_configs) != len(APPS):
            raise ValueError('You should be loading base configs (if any) so at this point there should be one config per app (or just the app).')
        base_interfaces = []
        for app, app_config in zip(APPS, app_configs):
            get_trapi_interface_fn = getattr(app, 'get_trapi_interface')
            base_interfaces.append(get_trapi_interface_fn(app_config))
        return base_interfaces

    def collect_app_queries(self, queries_list_of_lists):
        all_queries = []
        for queries in queries_list_of_lists:
            if type(queries) == list:
                all_queries.extend(queries)
            else:
                all_queries.append(queries)
        return all_queries

    def get_response(self, query):
        """ Main function of the processor that handles primary logic for obtaining
            a cached or calculated query response.
        """
        query_copy = query.get_copy()
        start_time = time.time()
        logger.info('Running query.')

        base_app_configs = self.get_app_configs(query_copy)
        base_interfaces = self.get_trapi_interfaces(base_app_configs)

        # Expand
        expand_queries = self.expand_batch_query(query)
       
        # For each app run the normalization and semops pipline

        # Make a copy of the expanded queries for each app
        app_queries = [[q.get_copy() for q in expand_queries] for _ in range(len(base_interfaces))]
        consistent_app_queries = []
        inconsistent_app_queries = []
        app_normalization_maps = []
        for interface, _expand_queries in zip(base_interfaces, app_queries):
            _ex_copy = []                
            # Normalize to Preferred Curies
            normalization_time = time.time()
            normalize_queries, normalization_map = self.normalize_to_preferred(
                    _expand_queries,
                    meta_knowledge_graph=interface.get_meta_knowledge_graph(),
                    with_normalization_map=True,
                    )
            app_normalization_maps.append(normalization_map)
            logger.info('Normalizaion time: {} seconds.'.format(time.time() - normalization_time))
            # Conflate
            conflation_time = time.time()
            
            conflate_queries = self.conflate_categories(
                    normalize_queries,
                    conflation_map=interface.get_conflation_map(),
                    )
            logger.info('Conflation time: {} seconds.'.format(time.time() - conflation_time))
            # Onto Expand
            onto_time = time.time()
            onto_queries = self.expand_supported_ontological_descendants(
                    conflate_queries,
                    curies_database=interface.get_curies(),
                    )
            logger.info('Ontological expansion time: {} seconds.'.format(time.time() - onto_time))
            # Semantic Ops Expand
            semops_time = time.time()
            semops_queries = self.expand_with_semantic_ops(
                    onto_queries,
                    meta_knowledge_graph=interface.get_meta_knowledge_graph(),
                    )
            logger.info('Sem ops time: {} seconds.'.format(time.time() - semops_time))
            # Filter out inconsistent queries
            filter_time = time.time()
            consistent_queries, inconsistent_queries = self.filter_queries_inconsistent_with_meta_knowledge_graph(
                    semops_queries,
                    meta_knowledge_graph=interface.get_meta_knowledge_graph(),
                    with_inconsistent_queries=True
                    )
            logger.info('Consistency filter time: {} seconds.'.format(time.time() - filter_time))

            logger.info('Number of consistent queries derived from passed query: {}.'.format(len(consistent_queries)))
            consistent_app_queries.append(consistent_queries)
            inconsistent_app_queries.append(inconsistent_queries)
        # Ensure that there are actually consistent queries that have been extracted
        if sum([len(_qs) for _qs in consistent_app_queries]) == 0:
            # Add all logs from inconsistent queries of all apps
            all_inconsistent_queries = self.collect_app_queries(inconsistent_queries)
            query_copy = self.add_logs_from_query_list(query_copy, all_inconsistent_queries)
            query_copy.set_status('Bad request. See description.')
            query_copy.set_description('Could not extract any supported queries from query graph.')
            self.add_transaction(query_copy)
            return JsonResponse(query_copy.to_dict())
        # Collect responses from each CHP app
        app_responses = []
        app_logs = []
        app_status = []
        app_descriptions = []
        for app, consistent_queries in zip(APPS, consistent_app_queries):
            get_app_response_fn = getattr(app, 'get_response')
            responses, logs, status, description = get_app_response_fn(consistent_queries)
            app_responses.extend(responses)
            app_logs.extend(logs)
            app_status.append(status)
            app_descriptions.append(description)
        # Check if any responses came back from any apps
        if  len(app_responses) == 0:
            # Add logs from consistent queries of all apps
            all_consistent_queries = self.collect_app_queries(consistent_app_queries)
            query_copy = self.add_logs_from_query_list(query_copy, all_consistent_queries)
            # Add app level logs
            query_copy.logger.add_logs(app_logs)
            query_copy.set_status('No results.')
            self.add_transaction(query_copy)
            return JsonResponse(query_copy.to_dict())

        # Add responses into database
        self.add_transactions(app_responses, app_names=[interface.get_name() for interface in base_interfaces])

        # Construct merged response
        response = self.merge_responses(query_copy, app_responses)

        # Now merge all app level log messages from each app
        response.logger.add_logs(app_logs)

        # Log any error messages for apps
        for app_name, status, description in zip(APPS, app_status, app_descriptions):
            if status != 'Success':
                response.warning('CHP App: {} reported a unsuccessful status: {} with description: {}'.format(
                    app_name, status, description)
                    )

        # Unnormalize with each apps normalization map
        unnormalized_response = response
        for normalization_map in app_normalization_maps:
            unnormalized_response = self.undo_normalization(unnormalized_response, normalization_map)
        
        logger.info('Constructed TRAPI response.')
        
        logger.info('Responded in {} seconds'.format(time.time() - start_time))
        unnormalized_response.set_status('Success')
       
        # Add workflow
        unnormalized_response.add_workflow("lookup")

        # Set the used biolink version
        unnormalized_response.biolink_version = TOOLKIT.get_model_version()

        # Add response to database
        self.add_transaction(unnormalized_response)
        
        return JsonResponse(unnormalized_response.to_dict())

    def add_logs_from_query_list(self, target_query, query_list):
        for query in query_list:
            target_query.logger.add_logs(query.logger.to_dict())
        return target_query

    def add_transaction(self, response, chp_app='dispatcher'):
        # Save the transaction
        transaction = Transaction(
            id = response.id,
            status = response.status,
            query = response.to_dict(),
            versions = settings.VERSIONS,
            chp_app = chp_app,
        )
        transaction.save()
        
    def add_transactions(self, responses, app_names):
        for response, chp_app in zip(responses, app_names):
            self.add_transaction(response, chp_app)
