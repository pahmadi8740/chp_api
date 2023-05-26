import logging
import time
import itertools
from copy import deepcopy
from re import A
from django.http import JsonResponse
from django.apps import apps
from django.conf import settings
from importlib import import_module
from collections import defaultdict

#from .curie_database import merge_curies_databases, CurieDatabase   ## NEED TO REMOVE
from .models import Transaction, App, DispatcherSettings, Template, TemplateMatch
from reasoner_pydantic import MetaKnowledgeGraph, Message, MetaEdge
from reasoner_pydantic.qgraph import QNode, QEdge

#from chp_utils.trapi_query_processor import BaseQueryProcessor   ## NEED TO REMOVE
#from trapi_model.meta_knowledge_graph import MetaKnowledgeGraph, merge_meta_knowledge_graphs   ## NEED TO REMOVE
#from trapi_model.query import Query   ## NEED TO REMOVE
#from trapi_model.biolink import TOOLKIT  ## NEED TO REMOVE


# Setup logging
logging.addLevelName(25, "NOTE")
# Add a special logging function
def note(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)
logging.Logger.note = note
logger = logging.getLogger(__name__)

# Import CHP Apps
APPS = [import_module(app+'.app_interface') for app in settings.INSTALLED_CHP_APPS]

class Dispatcher():
    def __init__(self, request, trapi_version):
        """ Base API Query Processor class used to abstract the processing infrastructure from
            the views. Inherits from the CHP Utilities Trapi Query Processor which handles
            node normalization, curie ontology expansion, and semantic operations.

            :param request: Incoming POST request with a TRAPI message.
            :type request: requests.request
        """
        self.request_data = deepcopy(request.data)

        self.trapi_version = trapi_version

    def get_meta_knowledge_graph(self):
        # Get current trapi and biolink versions
        dispatcher_settings = DispatcherSettings.load()
        merged_meta_kg = None
        for app, app_name in zip(APPS, settings.INSTALLED_CHP_APPS):
            app_db_obj = App.objects.get(name=app_name)
            # Load location from uploaded Zenodo files
            if app_db_obj.meta_knowledge_graph_zenodo_file:
                meta_kg = app_db_obj.meta_knowledge_graph_zenodo_file.load_file(base_url="https://sandbox.zenodo.org/api/records")
            # Load default location
            else:
                get_app_meta_kg_fn = getattr(app, 'get_meta_knowledge_graph')
                #TODO, when apps are set up correctly, they should return a pydantic_reasoner metakg. So I will have to remove .to_dict()
                # from deprecated trapi_model
                meta_kg = get_app_meta_kg_fn().to_dict()
            meta_kg = MetaKnowledgeGraph.parse_obj(meta_kg)
            if merged_meta_kg is None:
                merged_meta_kg = meta_kg
            else:
                merged_meta_kg.update(meta_kg)
        return merged_meta_kg

    def process_invalid_trapi(self, request):
        invalid_query_json = request.data
        invalid_query_json['status'] = 'Bad TRAPI.'
        return JsonResponse(invalid_query_json, status=400)

    def process_invalid_workflow(self, request, status_msg):
        invalid_query_json = request.data
        invalid_query_json['status'] = status_msg
        return JsonResponse(invalid_query_json, status=400)

    def process_request(self, request, trapi_version):
        """ Helper function that extracts the message from the request data.
        """
        logger.info('Starting query')
        message = Message.parse_obj(request.data['message'])
        logger.info('Message loaded')
        return message

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

    def extract_message_templates(self, Message):
        assert len(Message.query_graph.edges) == 1, 'CHP apps do not support multihop queries'
        subject = None
        predicates = []
        for edge_id, q_edge in Message.query_graph.edges.items():
            subject = q_edge.subject
            if q_edge.predicates is None:
                q_edge = QEdge(subject = q_edge.subject, predicates=['biolink:related_to'], object = q_edge.object)
            for predicate in q_edge.predicates:
                predicates.append(predicate)
        subject_categories = []
        object_categories = []
        for node_id, q_node in Message.query_graph.nodes.items():
            if q_node.categories is None:
                q_node = QNode(categories=['biolink:Entity'])
            for category in q_node.categories:
                if node_id == subject:
                    subject_categories.append(category)
                else:
                    object_categories.append(category)
        templates = []
        for edge in itertools.product(*[subject_categories, predicates, object_categories]):
            meta_edge = MetaEdge(subject=edge[0], predicate=edge[1], object=edge[2])
            templates.append(meta_edge)
        return templates

    def get_app_template_matches(self, app_name, templates):
        template_matches = []
        for template in templates:
            matches = TemplateMatch.objects.filter(template__app_name=app_name,
                                                   template__subject = template.subject,
                                                   template__object = template.object,
                                                   template__predicate = template.predicate)
            template_matches.extend(matches)
        return template_matches

    def apply_templates_to_message(self, message, matching_templates):
        consistent_queries = []
        for template in matching_templates:
            consistent_query = message.copy(deep=True)
            for edge_id, edge in consistent_query.query_graph.edges.items():
                edge.predicate = template.predicate
                subject_id = edge.subject
                object_id = edge.object
            consistent_query.query_graph.nodes[subject_id].categories = template.subject
            consistent_query.query_graph.nodes[object_id].categories = template.object
            consistent_queries.append(consistent_query)
        return consistent_queries

    def get_response(self, message):
        """ Main function of the processor that handles primary logic for obtaining
            a cached or calculated query response.
        """

        logger.info('Running message.')
        start_time = time.time()
        logger.info('Getting message templates.')
        message_templates = self.extract_message_templates(message)

        app_responses = []
        app_logs = []
        app_statuses = []
        app_descriptions = []
        for app, app_name in zip(APPS, settings.INSTALLED_CHP_APPS):
            logger.info('Checking template matches for {}'.format(app_name))
            matching_templates = self.get_app_template_matches(app_name, message_templates)
            logger.info('Detected {} matches for {}'.format(len(matching_templates), app_name))
            if len(matching_templates) > 0:
                logger.info('Constructing queries on matching templates')
                consistent_app_queries = self.apply_templates_to_message(message, matching_templates)
                logger.info('Sending {} consistent queries')
                get_app_response_fn = getattr(app, 'get_response')
                responses, logs, status, description = get_app_response_fn(consistent_app_queries)
                app_responses.extend(responses)
                app_logs.extend(logs)
                app_statuses.append(status)
                app_descriptions.append(description)
        print(app_responses)
        '''
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
        '''

    def add_logs_from_query_list(self, target_query, query_list):
        for query in query_list:
            target_query.logger.add_logs(query.logger.to_dict())
        return target_query

    def add_transaction(self, response, app_name='dispatcher'):
        app_db_obj = App.objects.get(name=app_name)
        # Save the transaction
        transaction = Transaction(
            id = response.id,
            status = response.status,
            query = response.to_dict(),
            versions = settings.VERSIONS,
            chp_app = app_db_obj,
        )
        transaction.save()
        
    def add_transactions(self, responses, app_names):
        for response, chp_app in zip(responses, app_names):
            self.add_transaction(response, chp_app)
