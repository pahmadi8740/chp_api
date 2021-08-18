import logging
import time
from collections import defaultdict
from django.http import JsonResponse

import chp
import chp_data
import chp_client
import chp_utils
import pybkb

from trapi_model.query import Query
from trapi_model.biolink.constants import *
from trapi_model.biolink import TOOLKIT
from chp.trapi_interface import TrapiInterface
from chp_utils.exceptions import SriOntologyKpException, SriNodeNormalizerException

from apis.chp_core.models import Transaction
from apis.chp_core.apps import ChpApiConfig, ChpBreastApiConfig, ChpBrainApiConfig, ChpLungApiConfig

# Setup logging
logging.addLevelName(25, "NOTE")
# Add a special logging function
def note(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)
logging.Logger.note = note
logger = logging.getLogger(__name__)

class ChpCoreQueryProcessorMixin:
    @staticmethod
    def get_app_config(request):
        # Get Host
        host = request.headers['Host']
        
        # Parse host name
        host_parse = host.split('.')
        
        # API subdomain is the ChpConfig to use.
        subdomain = host_parse[0]
        passed_subdomain = True
        # Get CHP Config
        if 'breast' in subdomain:
            chp_config = ChpBreastApiConfig
            logger.info('Breast cancer subdomain hit.')
        elif 'brain' in subdomain:
            chp_config = ChpBrainApiConfig
            logger.info('Brain cancer subdomain hit.')
        elif 'lung' in subdomain:
            chp_config = ChpLungApiConfig
            logger.info('Lung cancer subdomain hit.')
        else:
            chp_config = ChpApiConfig
            passed_subdomain = False
        return chp_config, passed_subdomain

    def get_versions(self):
        return { 
                'chp' : chp.__version__,
                'chp_client' : chp_client.__version__,
                'chp_data' : chp_data.__version__,
                'pybkb' : pybkb.__version__,
                'chp_utils': chp_utils.__version__,
                }

    def process_request(self, request):
        """ Helper function that extracts the query from the message.
        """
        logger.info('Starting query.')
        
        query = Query.load(self.trapi_version, biolink_version=None, query=request.data)

        # Setup query in Base Processor
        self.setup_query(query)

        logger.info('Query loaded')
        
        return query

    def get_disease_nodes(self, query):
        disease_node_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_DISEASE_ENTITY])
        if disease_node_ids is not None:
            disease_nodes = [query.message.query_graph.nodes[_id] for _id in disease_node_ids]
            return disease_nodes
        return None

    def get_disease_specific_config(self, disease_node):
        if disease_node.ids[0] == 'MONDO:0005061':
            chp_config = ChpLungApiConfig
        elif disease_node.ids[0] == 'MONDO:0001657':
            chp_config = ChpBrainApiConfig
        elif disease_node.ids[0] == 'MONDO:0007254':
            chp_config = ChpBreastApiConfig
        else:
            chp_config = ChpApiConfig
        return chp_config

    def setup_queries_based_on_disease_interfaces(self, queries):
        config_dict = defaultdict(list)
        for query in queries:
            disease_nodes = self.get_disease_nodes(query)
            if disease_nodes is not None:
                if len(disease_nodes) > 1:
                    query.info('Using {} config.'.format(ChpApiConfig.name))
                    config_dict[ChpApiConfig].append(query)
                    continue
                chp_config = self.get_disease_specific_config(disease_nodes[0])
                query.info('Using {} config.'.format(chp_config.name))
                config_dict[chp_config].append(query)
            else:
                config_dict[ChpApiConfig].append(query)
                continue
        interface_dict = {self.get_trapi_interface(chp_config): _queries for chp_config, _queries in config_dict.items()}
        return interface_dict

    def get_trapi_interface(self, chp_config):
        return TrapiInterface(
            hosts_filename=chp_config.hosts_filename,
            num_processes_per_host=chp_config.num_processes_per_host,
            bkb_handler=chp_config.bkb_handler,
            joint_reasoner=chp_config.joint_reasoner,
            dynamic_reasoner=chp_config.dynamic_reasoner,
            )

    def get_response(self, query):
        """ Main function of the processor that handles primary logic for obtaining
            a cached or calculated query response.
        """
        query_copy = query.get_copy()
        start_time = time.time()
        logger.info('Running query.')
            
        # Instaniate CHP TRAPI Interface
        interface = TrapiInterface(
            hosts_filename=self.chp_config.hosts_filename,
            num_processes_per_host=self.chp_config.num_processes_per_host,
            bkb_handler=self.chp_config.bkb_handler,
            joint_reasoner=self.chp_config.joint_reasoner,
            dynamic_reasoner=self.chp_config.dynamic_reasoner,
        )
        
        # Expand
        expand_queries = self.expand_batch_query(query)
        # Normalize to Preferred Curies
        normalization_time = time.time()
        normalize_queries, normalization_map = self.normalize_to_preferred(
                expand_queries,
                meta_knowledge_graph=interface.get_meta_knowledge_graph(),
                with_normalization_map=True,
                )

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

        # Ensure that there are actually consistent queries that have been extracted
        if len(consistent_queries) == 0:
            # Add all logs from inconsistent queries
            query_copy = self.add_logs_from_query_list(query_copy, inconsistent_queries)
            query_copy.set_status('Bad request. See description.')
            query_copy.set_description('Could not extract any supported queries from query graph.')
            self.add_transaction(query_copy)
            return JsonResponse(query_copy.to_dict())
            
        # Get disease specific interfaces if a subdomain was not used
        interface_dict = self.setup_queries_based_on_disease_interfaces(consistent_queries)

        logger.info('Number of consistent queries derived from passed query: {}.'.format(len(consistent_queries)))
        # Setup for CHP inferencing
        try:
            setup_time = time.time()
            for interface, queries in interface_dict.items():
                interface.setup_trapi_queries(queries)
            logger.info('Trapi Interface setup time: {} seconds.'.format(time.time() - setup_time))
        except Exception as ex:
            # Add logs from consistent queries
            query_copy = self.add_logs_from_query_list(query_copy, consistent_queries)
            # Add logs from interfaces level
            for interface in interface_dict:
                query_copy.logger.add_logs(interface.logger.to_dict())
            query_copy.set_status('Bad request. See description.')
            query_copy.set_description('Problem during interface setup. ' + str(ex))
            self.add_transaction(query_copy)
            return JsonResponse(query_copy.to_dict())
        
        # Build CHP queries
        try:
            build_time = time.time()
            for interface in interface_dict:
                interface.build_chp_queries()
            logger.info('CHP query build time: {} seconds.'.format(time.time() - build_time))
        except Exception as ex:
            # Add logs from consistent queries
            query_copy = self.add_logs_from_query_list(query_copy, consistent_queries)
            # Add logs from interfaces level
            for interface in interface_dict:
                query_copy.logger.add_logs(interface.logger.to_dict())
            query_copy.set_status('Bad request. See description.')
            query_copy.set_description('Problem during CHP query building. '+ str(ex))
            self.add_transaction(query_copy)
            return JsonResponse(query_copy.to_dict())

        logger.info('Built Queries.')
        # Run queries
        try:
            reasoning_start_time = time.time()
            for interface in interface_dict:
                interface.run_chp_queries()
            logger.info('Completed Reasoning in {} seconds.'.format(time.time() - reasoning_start_time))
        except Exception as ex:
            # Add logs from consistent queries
            query_copy = self.add_logs_from_query_list(query_copy, consistent_queries)
            # Add logs from interfaces level
            for interface in interface_dict:
                query_copy.logger.add_logs(interface.logger.to_dict())
            query_copy.set_status('Unexpected error. See description.')
            query_copy.set_description('Problem during reasoning. ' + str(ex))
            self.add_transaction(query_copy)
            # Report critical error to logs
            logger.critical('Error during reasoning. Check query: {}'.format(query_copy.id))
            return JsonResponse(query_copy.to_dict())

        # Construct Response
        responses = []
        for interface in interface_dict:
            responses.extend(interface.construct_trapi_responses())
        
        # Check if any responses came back
        if len(responses) == 0:
            # Add logs from consistent queries
            query_copy = self.add_logs_from_query_list(query_copy, consistent_queries)
            # Add logs from interfaces level
            for interface in interface_dict:
                query_copy.logger.add_logs(interface.logger.to_dict())
            query_copy.set_status('No results.')
            self.add_transaction(query_copy)
            return JsonResponse(query_copy.to_dict())

        # Add responses into database
        self.add_transactions(responses)

        # Construct merged response
        response = self.merge_responses(query_copy, responses)

        # Now merge all interface level log messages from each interface
        for interface in interface_dict:
            response.logger.add_logs(interface.logger.to_dict())

        # Unnormalize
        unnormalized_response = self.undo_normalization(response, normalization_map)
        
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

    def add_transaction(self, response):
        # Save the transaction
        transaction = Transaction(
            id = response.id,
            status = response.status,
            query = response.to_dict(),
            chp_version = chp.__version__,
            chp_data_version = chp_data.__version__,
            pybkb_version = pybkb.__version__,
            chp_client_version = chp_client.__version__,
            chp_utils_version = chp_utils.__version__,
        )
        transaction.save()
        
