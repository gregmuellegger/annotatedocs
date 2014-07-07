import unittest
from rdflib import Graph, OWL, Namespace
from annotatedocs.reasoner import owlrl, get_inferred


EX = Namespace('http://example.com/')


class OWLRLTests(unittest.TestCase):
    def reason(self, data):
        graph = Graph()
        graph.parse(data='''
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix : <http://example.com/> .

            {data}
        '''.format(data=data), format='turtle')

        owlrl(graph)
        return graph

    def test_same_as(self):
        graph = self.reason('''
            :A owl:sameAs :B .
        ''')

        self.assertTrue(
            (EX.B, OWL.sameAs, EX.A) in graph)

    def test_transitive_property(self):
        graph = Graph()
        graph = self.reason('''
            :A :hasAncestor :B .
            :B :hasAncestor :C .
            :hasAncestor a owl:TransitiveProperty .
        ''')

        self.assertTrue(
            (EX.A, EX.hasAncestor, EX.C) in graph)

    def test_subpropertyof(self):
        graph = self.reason('''
            :A :hasAncestor :B .
            :hasAncestor rdfs:subPropertyOf :hasParent .
        ''')

        self.assertTrue(
            (EX.A, EX.hasParent, EX.B) in graph)

    def test_transitive_subpropertyof(self):
        graph = self.reason('''
            :A :hasParent :B .
            :B :hasParent :C .

            :hasParent rdfs:subPropertyOf :hasAncestor .
            :hasAncestor a owl:TransitiveProperty .
        ''')

        self.assertTrue(
            (EX.A, EX.hasAncestor, EX.C) in graph)
        self.assertFalse(
            (EX.A, EX.hasParent, EX.C) in graph)


class InferTests(unittest.TestCase):
    def reason(self, data):
        graph = Graph()
        graph.parse(data='''
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix ex: <http://example.com/> .

            {data}
        '''.format(data=data), format='turtle')

        return get_inferred(graph)

    def test_same_as(self):
        graph = self.reason('''
            ex:A owl:sameAs ex:B .
        ''')

        self.assertTrue(
            (EX.B, OWL.sameAs, EX.A) in graph)
