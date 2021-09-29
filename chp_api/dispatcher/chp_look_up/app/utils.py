from sys import path
from django.http import response
from django.http.response import JsonResponse
from trapi_model import knowledge_graph
from trapi_model.query import Query
from trapi_model.biolink.constants import *
from .models import *
from trapi_model.knowledge_graph import KnowledgeGraph, KNode, KEdge


class QueryProcessor:
    def __init__(self, query) -> None:
        self.query = query
        self.response = None
    
    def build_response(self) -> None:
        raise NotImplementedError
    def get_response(self) -> JsonResponse:
        raise NotImplementedError
    def extract_primary_key() -> str:
        raise NotImplementedError

class PathwayToGeneWildcardQueryProcessor(QueryProcessor):
    def __init__(self, query) -> None:
        super().__init__(query)
        self.pathway_nodes_id = query.message.query_graph.find_nodes(categories=[BIOLINK_PATHWAY_ENTITY])
        self.pathway_nodes_id = list(self.pathway_nodes_id)[0]
        pathway_node = query.message.query_graph.nodes.get(self.pathway_nodes_id)
        self.pathway_curie = (pathway_node.ids[0])

        #TODO: implement querying      
        self.response = 'dd'
    def getResponse(self):
        return JsonResponse(self.response, safe=False)

class GeneToPathwayWildcardQueryProcessor(QueryProcessor):
    def __init__(self, query) -> None:
        super().__init__(query)

        self.gene_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_GENE_ENTITY])
        self.gene_nodes_ids = list(self.gene_nodes_ids)[0]
        gene_node = query.message.query_graph.nodes.get(self.gene_nodes_ids)
        self.gene_curie = (gene_node.ids[0])

        self.pathways = GeneToPathway.objects.get(gene__exact=self.gene_curie).get_result()
        print(self.pathways)
        self.build_response()
    
    def build_response(self) -> None:
        knowledge_graph = KnowledgeGraph()
        gene_count = 0
        knowledge_graph.add_node(curie=self.gene_curie, categories="biolink:Gene", name=self.gene_curie)
        

        for pathway in self.pathways:
            gene_count = gene_count + 1
            print(pathway)
            knowledge_graph.add_node(curie=pathway, categories="biolink:Pathway", name=pathway)
            knowledge_graph.add_edge(k_subject='n0', k_object="n{}".format(gene_count), predicate="biolink:participates_in")
        
        self.response = knowledge_graph.to_dict()

    def getResponse(self) -> JsonResponse:
        return JsonResponse(self.response, safe=False)

class InvalidQueryProcessor(QueryProcessor):
    def __init__(self,query) -> None:
        super().__init__(query)

    def getResponse(self):
        return JsonResponse('invalid query type', safe=False)




class QueryIdentifier:
    """
    Identifies the type of query being passed so that the appropriate query processor7 may be applied to the query
    
    :param
    """
    
    @staticmethod
    def getQueryProcessor(request) -> QueryProcessor:
        def isGeneToPathwayWildcardQuery(query:Query)->bool:
            """
            Identifies if a query is a gene to pathway query
            """
            #check genes
            pathway_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_PATHWAY_ENTITY])
            gene_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_GENE_ENTITY])
            
            if pathway_nodes_ids is None:
                return False
            if gene_nodes_ids is None:
                return False
            if len(pathway_nodes_ids) != 1:
                return False
            if len(gene_nodes_ids) != 1:
                return False
            
            #check edge
            edges = query.message.query_graph.edges

            if len(edges) != 1:
                return False
            id = list(edges.keys())[0]
            edge = edges.get(id)
            
            #check predicate
            predicates = edge.predicates
            if len(predicates) != 1:
                return False
            predicate = predicates[0]
            predicate = predicate.passed_name

            if predicate != 'biolink:participates_in':
                return False

            #return True if all is swell
            return True
        
        def isPathwayToGeneWildcardQuery(query:Query)->bool:
            """
            Identifies if a query is a pathway to gene query
            """
            pathway_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_PATHWAY_ENTITY])
            gene_nodes_ids = query.message.query_graph.find_nodes(categories=[BIOLINK_GENE_ENTITY])

            if pathway_nodes_ids is None:
                return False
            if gene_nodes_ids is None:
                return False
            if len(pathway_nodes_ids) != 1:
                return False
            if len(gene_nodes_ids) != 1:
                return False
            
            #check edge
            edges = query.message.query_graph.edges

            if len(edges) != 1:
                return False
            id = list(edges.keys())[0]
            edge = edges.get(id)
            
            #check predicate
            predicates = edge.predicates
            if len(predicates) != 1:
                return False
            predicate = predicates[0]
            predicate = predicate.passed_name

            if predicate != 'biolink:has_participant':
                return False

            #return True if all is swell
            return True

         #Load in query from 
        
        query = Query.load('1.1', biolink_version=None, query=request.data, metakgValidation=False, semanticOperations=False)
        
        query_processor = None
        if isPathwayToGeneWildcardQuery(query):
            query_processor = PathwayToGeneWildcardQueryProcessor(query)
        elif isGeneToPathwayWildcardQuery(query):
            query_processor = GeneToPathwayWildcardQueryProcessor(query)
        else:
            query_processor = InvalidQueryProcessor(query)
        return query_processor