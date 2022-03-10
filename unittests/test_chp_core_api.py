import pickle
import json
import logging
import unittest
import requests

from trapi_model import *
LOCAL_URL = 'http://localhost:8000'
#LOCAL_URL = 'http://localhost:80'
#LOCAL_URL = 'http://chp-dev.thayer.dartmouth.edu'

class TestChpApi(unittest.TestCase):

    def setUp(self):
        self.query_endpoint = '/query/'
        self.curies_endpoint = '/curies/'
        self.meta_knowledge_graph_endpoint = '/meta_knowledge_graph/'

    @staticmethod
    def _get(url, params=None):
        params = params or {}
        res = requests.get(url, json=params)
        print(res.content)
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
            return ret, res.status_code

    def _print_query(query):
        print(json.dumps(query, indent=2))

    def test_curies(self):
        url = LOCAL_URL + self.curies_endpoint
        resp = self._get(url)

    def test_meta_knowledge_graph(self):
        url = LOCAL_URL + self.meta_knowledge_graph_endpoint
        resp = self._get(url)

    def test_standard_onehop_query(self):
        with open('query_samples/onehop/no-normalization/standard_queries.json', 'rb') as f_:
            queries = json.load(f_)
        for query in queries:
            test_description = query.pop("test_description", None)
            print(test_description)
            url = LOCAL_URL + self.query_endpoint
            resp, status = self._post(url, query)
            print(resp["id"])
            self.assertEqual(status, 200)
    
    
    def test_wildcard_onehop_query(self):
        with open('query_samples/onehop/no-normalization/wildcard_queries.json', 'rb') as f_:
            queries = json.load(f_)
        for query in queries:
            test_description = query.pop("test_description", None)
            print(test_description)
            url = LOCAL_URL + self.query_endpoint
            resp, status = self._post(url, query)
            print(resp["id"])
            self.assertEqual(status, 200)
    
    def test_standard_onehop_with_normalization_query(self):
        with open('query_samples/onehop/normalization/standard_batch_onehop_queries.json', 'rb') as f_:
            queries = json.load(f_)
        for query in queries:
            test_description = query.pop("test_description", None)
            print(test_description)
            url = LOCAL_URL + self.query_endpoint
            resp, status = self._post(url, query)
            print(resp["id"])
            self.assertEqual(status, 200)
    

    # Error testing
    '''
    def test_more_than_one_contribution(self):
        with open('query_samples/error_samples/test_more_than_one_contribution.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_more_than_one_disease(self):
        with open('query_samples/error_samples/test_more_than_one_disease.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_more_than_one_phenotype(self):
        with open('query_samples/error_samples/test_more_than_one_phenotype.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_more_than_one_disease(self):
        with open('query_samples/error_samples/test_more_than_one_disease.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_no_disease(self):
        with open('query_samples/error_samples/test_no_disease.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_no_target(self):
        with open('query_samples/error_samples/test_no_target.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_drug_to_disease_default(self):
        with open('query_samples/error_samples/test_illegal_drug_to_disease_default.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_gene_to_disease_default(self):
        with open('query_samples/error_samples/test_illegal_gene_to_disease_default.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_disease_to_phenotype_default(self):
        with open('query_samples/error_samples/test_illegal_disease_to_phenotype_default.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_edge_default(self):
        with open('query_samples/error_samples/test_illegal_edge_default.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_gene_to_disease_wildcard(self):
        with open('query_samples/error_samples/test_illegal_gene_to_disease_wildcard.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_drug_to_disease_wildcard(self):
        with open('query_samples/error_samples/test_illegal_drug_to_disease_wildcard.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_disease_to_phenotype_wildcard(self):
        with open('query_samples/error_samples/test_illegal_disease_to_phenotype_wildcard.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_edge_wildcard(self):
        with open('query_samples/error_samples/test_illegal_edge_wildcard.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_drug_to_disease_one_hop(self):
        with open('query_samples/error_samples/test_illegal_drug_to_disease_one_hop.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_illegal_disease_to_phenotype_one_hop(self):
        with open('query_samples/error_samples/test_illegal_disease_to_phenotype_one_hop.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)
    '''
if __name__ == '__main__':
    unittest.main()
