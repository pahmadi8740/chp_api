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

    def test_unknown_edge_default(self):
        with open('query_samples/error_samples/test_unknown_edge_default.pk', 'rb') as f_:
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

    def test_unknown_edge_wildcard(self):
        with open('query_samples/error_samples/test_unknown_edge_wildcard.pk', 'rb') as f_:
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

    def test_illegal_gene_to_drug_one_hop(self):
        with open('query_samples/error_samples/test_illegal_gene_to_drug_one_hop.pk', 'rb') as f_:
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

    def test_backwards_contribution_node_one_hop(self):
        with open('query_samples/error_samples/test_backwards_contribution_node_one_hop.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

    def test_unknown_edge_one_hop(self):
        with open('query_samples/error_samples/test_unknown_edge_one_hop.pk', 'rb') as f_:
            query = pickle.load(f_)
        query = {'message':query}
        url = LOCAL_URL + self.query_endpoint
        resp = self._post(url,query)

if __name__ == '__main__':
    unittest.main()
