import pickle
import json
import logging
import unittest
import requests

LOCAL_URL = 'http://127.0.0.1:8000'
#LOCAL_URL = 'http://localhost:80'
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

    def test_single_default_query(self):
        with open('query_samples/test_reasoner_coulomb_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_batch_default_query(self):
        with open('query_samples/test_reasoner_coulomb_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_single_gene_wildcard_query(self):
        with open('query_samples/random_gene_wildcard_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_batch_gene_wildcard_query(self):
        with open('query_samples/random_gene_wildcard_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_single_drug_wildcard_query(self):
        with open('query_samples/random_drug_wildcard_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_batch_drug_wildcard_query(self):
        with open('query_samples/random_drug_wildcard_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_single_gene_onehop_query(self):
        with open('query_samples/random_gene_one_hop_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)
        print(json.dumps(resp, indent=2))

    def test_batch_gene_onehop_query(self):
        with open('query_samples/random_gene_one_hop_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)

    def test_single_drug_onehop_query(self):
        with open('query_samples/random_drug_one_hop_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        query = queries[0]
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url, query)

    def test_batch_drug_onehop_query(self):
        with open('query_samples/random_drug_one_hop_queries.pk', 'rb') as f_:
            queries = pickle.load(f_)
        wrapped_queries = self._wrap_batch_queries(queries)
        url = LOCAL_URL + self.query_all_endpoint
        resp = self._post(url, wrapped_queries)
