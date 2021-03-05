import pickle
import json
import logging
import unittest
import requests

#LOCAL_URL = 'http://127.0.0.1:8000'
LOCAL_URL = 'http://localhost:80'
#LOCAL_URL = 'http://chp.thayer.dartmouth.edu'

class TestChpApi(unittest.TestCase):

    def setUp(self):
        self.query_endpoint = '/query/'
        self.query_all_endpoint = '/queryall/'
        self.curies_endpoint = '/curies/'
        self.predicates_endpoint = '/predicates/'
        self.constants_endpoint = '/constants/'

    @staticmethod
    def _get(url, params=None):
        params = params or {}
        res = requests.get(url, json=params)
        ret = res.json()
        return ret

    @staticmethod
    def _post(url, params):
        res = requests.post(url, json=params)
        if res.status_code != 200:
            print(res.status_code)
            print(res.content)
            return res.content
        else:
            ret = res.json()
            return ret

    @staticmethod
    def _wrap_batch_queries(queries):
        wrapped_queries = {"message": []}
        for q in queries:
            q_message = q.pop('message')
            wrapped_queries["message"].append(q_message)
        return wrapped_queries

    def _print_query(query):
        print(json.dumps(query, indent=2))

    def test_curies(self):
        url = LOCAL_URL + self.curies_endpoint
        resp = self._get(url)

    def test_predicates(self):
        url = LOCAL_URL + self.predicates_endpoint
        resp = self._get(url)
    
    def test_constants(self):
        url = LOCAL_URL + self.constants_endpoint
        resp = self._get(url)
        print(resp)

    def test_bad_single_default_query(self):
        with open('query_samples/test_reasoner_coulomb_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_bad_batch_default_query(self):
        with open('query_samples/test_reasoner_coulomb_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_bad_single_gene_wildcard_query(self):
        with open('query_samples/random_gene_wildcard_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_bad_batch_gene_wildcard_query(self):
        with open('query_samples/random_gene_wildcard_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_bad_single_drug_wildcard_query(self):
        with open('query_samples/random_drug_wildcard_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_bad_batch_drug_wildcard_query(self):
        with open('query_samples/random_drug_wildcard_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_bad_single_gene_onehop_query(self):
        with open('query_samples/random_gene_one_hop_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_bad_batch_gene_onehop_query(self):
        with open('query_samples/random_gene_one_hop_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_bad_single_drug_onehop_query(self):
        with open('query_samples/random_drug_one_hop_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_bad_batch_drug_onehop_query(self):
        with open('query_samples/random_drug_one_hop_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_normal_two_genes_and_drug(self):
        # get constants
        url = LOCAL_URL + self.constants_endpoint
        constants = self._get(url)

        # empty response
        reasoner_std = { "query_graph": dict()
                       }

        # empty query graph
        reasoner_std["query_graph"] = { "edges": dict(),
                                        "nodes": dict()
                                      }

        # add in evidence gene
        gene1 = ('RAF1', 'ENSEMBL:ENSG00000132155')
        reasoner_std['query_graph']['nodes']['n0'] = { 'category':constants['BIOLINK_GENE'],
                                                       'id':'{}'.format(gene1[1])
                                                     }

        gene2 = ('BRCA1', 'ENSEMBL:ENSG00000012048')
        reasoner_std['query_graph']['nodes']['n1'] = { 'category':constants['BIOLINK_GENE'],
                                                       'id':'{}'.format(gene2[1])
                                                     }
        # add in evidence drug
        drug = ('CYCLOPHOSPHAMIDE', 'CHEMBL:CHEMBL88')
        reasoner_std['query_graph']['nodes']['n2'] = { 'category':constants['BIOLINK_DRUG'],
                                                       'id':'{}'.format(drug[1])
                                                     }
        # add in disease node
        disease = ('Breast_Cancer', 'MONDO:0007254')
        reasoner_std['query_graph']['nodes']['n3'] = { 'category':constants['BIOLINK_DISEASE'],
                                                       'id':'{}'.format(disease[1])
                                                     }
        # add target survival node
        phenotype = ('Survival_Time', 'EFO:0000714')
        reasoner_std['query_graph']['nodes']['n4'] = { 'category': constants['BIOLINK_PHENOTYPIC_FEATURE'],
                                                       'id': '{}'.format(phenotype[1]),
                                                     }
        # link genes/drugs to disease
        reasoner_std['query_graph']['edges']['e0'] = { 'predicate':constants['BIOLINK_GENE_TO_DISEASE_PREDICATE'],
                                                       'subject': 'n0',
                                                       'object': 'n3'
                                                     }
        reasoner_std['query_graph']['edges']['e1'] = { 'predicate':constants['BIOLINK_GENE_TO_DISEASE_PREDICATE'],
                                                       'subject': 'n1',
                                                       'object': 'n3'
                                                     }
        reasoner_std['query_graph']['edges']['e2'] = { 'predicate':constants['BIOLINK_CHEMICAL_TO_DISEASE_OR_PHENOTYPIC_FEATURE_PREDICATE'],
                                                       'subject': 'n2',
                                                       'object': 'n3'
                                                     }
        # link disease to target
        reasoner_std['query_graph']['edges']['e3'] = { 'predicate':constants['BIOLINK_DISEASE_TO_PHENOTYPIC_FEATURE_PREDICATE'],
                                                       'subject': 'n3',
                                                       'object': 'n4',
                                                       'properties': { 'qualifier':'>=',
                                                                       'days':970
                                                                     }
                                                     }
        query = {'message':reasoner_std}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_wildcard_drug(self):
        # get constants
        url = LOCAL_URL + self.constants_endpoint
        constants = self._get(url)

        # empty response
        reasoner_std = { "query_graph": {}
                       }
        # empty query graph
        reasoner_std["query_graph"] = { "edges": {},
                                        "nodes": {}
                                      }

        # add in evidence drug
        drug = ('CYCLOPHOSPHAMIDE', 'CHEMBL:CHEMBL88')
        reasoner_std['query_graph']['nodes']['n0'] = {
                                                      'category':constants['BIOLINK_DRUG'],
                                                      'id':'{}'.format(drug[1])
                                                     }

        # add in gene node (to be filled by contribution analysis
        reasoner_std['query_graph']['nodes']['n1'] = {
                                                      'category':constants['BIOLINK_GENE']
                                                     }

        #add in disease node
        disease = ('Breast_Cancer', 'MONDO:0007254')
        reasoner_std['query_graph']['nodes']['n2'] = {
                                                      'category':constants['BIOLINK_DISEASE'],
                                                      'id':'{}'.format(disease[1])
                                                     }

        # add target survival node
        phenotype = ('Survival_Time', 'EFO:0000714')
        reasoner_std['query_graph']['nodes']['n3'] = {
                                                      'category': constants['BIOLINK_PHENOTYPIC_FEATURE'],
                                                      'id': '{}'.format(phenotype[1]),
                                                     }

        # link disease to target survival node
        reasoner_std['query_graph']['edges']['e0'] = {
                                                      'predicate':constants['BIOLINK_DISEASE_TO_PHENOTYPIC_FEATURE_PREDICATE'],
                                                      'subject':'n2',
                                                      'object':'n3',
                                                      'properties': {
                                                                     'qualifier': '>=',
                                                                     'days': 1000
                                                                    }
                                                     }

        # link genes/drugs to disease
        reasoner_std['query_graph']['edges']['e1'] = {
                                                      'predicate':constants['BIOLINK_GENE_TO_DISEASE_PREDICATE'],
                                                      'subject': 'n1',
                                                      'object': 'n2'
                                                     }
        reasoner_std['query_graph']['edges']['e2'] = {
                                                      'predicate':constants['BIOLINK_CHEMICAL_TO_DISEASE_OR_PHENOTYPIC_FEATURE_PREDICATE'],
                                                      'subject': 'n0',
                                                      'object': 'n2'
                                                     }
        query = {'message':reasoner_std}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_one_hop_gene(self):
        # get constants
        url = LOCAL_URL + self.constants_endpoint
        constants = self._get(url)

        # empty response
        reasoner_std = { "query_graph": dict()}
        # empty query graph
        reasoner_std["query_graph"] = { "edges": {},
                                        "nodes": {}
                                      }
        # add in evidence drug
        drug = ('CYCLOPHOSPHAMIDE', 'CHEMBL:CHEMBL88')
        reasoner_std['query_graph']['nodes']['n{}'.format('0')] = {
                                                      'category':constants['BIOLINK_DRUG'],
                                                      'id':'{}'.format(drug[1])
        }

        # add in gene node (to be filled by contribution analysis
        reasoner_std['query_graph']['nodes']['n{}'.format('1')] = {
                                                      'category':constants['BIOLINK_GENE'],
                                                   }

        # link genes/drugs to disease
        reasoner_std['query_graph']['edges']['e{}'.format(0)] = {
                                                       'predicate':constants['BIOLINK_CHEMICAL_TO_GENE_PREDICATE'],
                                                       'subject': 'n1',
                                                       'object': 'n0'
                                                     }
        query = {'message':reasoner_std}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

if __name__ == '__main__':
    unittest.main()
