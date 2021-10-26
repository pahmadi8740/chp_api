from chp_look_up.trapi_interface import TrapiInterface
from chp_look_up.app.apps import *
from trapi_model.meta_knowledge_graph import MetaKnowledgeGraph
from chp_utils.curie_database import CurieDatabase
from chp_utils.conflation import ConflationMap
import os

def get_app_config(query):
    return ChpLookUpConfig

def get_trapi_interface(chp_look_up_config = get_app_config(None)):
    return TrapiInterface(trapi_version='1.2')

def get_meta_knowledge_graph() -> MetaKnowledgeGraph:
    interface = get_trapi_interface()
    return interface.get_meta_knowledge_graph()

def get_curies() -> CurieDatabase:
    interface = get_trapi_interface()
    return interface.get_curies()

def get_conflation_map() -> ConflationMap:
    interface = get_trapi_interface()
    return interface.get_conflation_map()
    
def get_response(consistent_queries):
    """ Should return app responses plus app_logs, status, and description information.
    """
    interface = get_trapi_interface()
    identified_queries_tuple = interface.identify_queries(consistent_queries)
    database_results_with_query_tuple = interface.query_database(identified_queries_tuple)