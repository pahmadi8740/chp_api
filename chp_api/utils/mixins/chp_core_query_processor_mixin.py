from trapi_model.query import Query

from apis.chp_core.models import Transaction
from apis.chp_core.apps import ChpApiConfig, ChpBreastApiConfig, ChpBrainApiConfig, ChpLungApiConfig


class ChpCoreQueryProcessorMixin:
    def get_chp_config(request, query):
        # Get Host
        host = request.headers['Host']
        
        # Parse host name
        host_parse = host.split('.')
        
        # API subdomain is the ChpConfig to use.
        subdomain = host_parse[0]

        # Extract disease nodes
        disease_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_DISEASE_ENTITY])
        
        # Get CHP Config
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
        return chp_config

    @staticmethod
    def _process_request(request, trapi_version='1.1'):
        """ Helper function that extracts the query from the message.
        """
        logger.note('Starting query.')
        
        data = request.data
        query = Query.load(trapi_version, biolink_version=None, query=data)
        
        logger.note('Query loaded')
        
        chp_config = self.get_chp_config(request, query)
        
        return query, chp_config

    def get_response_to_query(self):
        """ Main function of the processor that handles primary logic for obtaining
            a cached or calculated query response.
        """
        if self.request_process_failure_response is not None:
            return JsonResponse(self.request_process_failure_response)

        start_time = time.time()
        if self.query is not None:
            logger.note('Running query.')

            # Extract batch queries
            queries = self.expand_batch_query(query)
            
            # Normalize queries with SRI Node Normalizer
            queries, normalization_map = self.normalize_to_preferred(queries)
            
            # Fill Biolink categories
            query = self.fill_biolink_categories(query)



            # Expand with supported ontological descendents
            queries = self.expand_supported_ontological_descendents(queries)

            # Expand queries with semantic operations
            queries = self.expand_with_semantic_ops(queries)

            try:
                # Instaniate CHP TRAPI Interface
                interface = TrapiInterface(
                    queries=queries,
                    hosts_filename=self.chp_config.hosts_filename,
                    num_processes_per_host=self.chp_config.num_processes_per_host,
                    bkb_handler=self.chp_config.bkb_handler,
                    joint_reasoner=self.chp_config.joint_reasoner,
                    dynamic_reasoner=self.chp_config.dynamic_reasoner,
                )

                # Build queries
                interface.build_chp_queries()
            except Exception as e:
                self.data_copy['status'] = 'Bad request.' + str(e)
                return JsonResponse(self.data_copy)

            logger.note('Built Queries.')
            # Run queries
            try:
                reasoning_start_time = time.time()
                interface.run_chp_queries()
                logger.note('Completed Reasoning in {} seconds.'.format(time.time() - reasoning_start_time))
            except Exception as e:
                logger.critical('Error during reasoning.')
                self.data_copy['status'] = 'Unexpected error.' + str(e)
                return JsonResponse(self.data_copy)

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
        #response_dict['message']['query_graph']=self.data_copy['message']['query_graph']
        response_dict['status'] = 'Success'
        return JsonResponse(response_dict)
