# -*- coding: utf-8 -*-
import os
import logging
import pickle
import unittest
from rdflib import RDF, RDFS, Literal
from docutils import nodes
from annotatedocs import doctree2rdf
from annotatedocs.doctree2rdf import Doctree2RDF, ONTOLOGY_NAMESPACE
from annotatedocs.reasoner import owlrl


logger = logging.getLogger(__name__)


O = ONTOLOGY_NAMESPACE


def load_doctree(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(base_path, 'sampledocs')
    path = os.path.join(
        base_path,
        '_build',
        'doctrees',
        '{}.doctree'.format(filename))

    with open(path, 'rb') as file:
        document = pickle.load(file)
        if not isinstance(document, nodes.document):
            raise Exception('Expected a document in file.')
        document.reporter = logger
        return document


class Doctree2RDFTests(unittest.TestCase):
    def test_title_text(self):
        doctree = load_doctree('installation')
        parser = Doctree2RDF(doctree)
        D = parser.document_namespace

        graph = parser.get_graph()
        graph += doctree2rdf.get_ontology()
        owlrl(graph)

        result = list(graph.triples((None, RDFS.label, Literal('Second title'))))
        self.assertEqual(len(result), 1)
        subject, __, __ = result[0]

        self.assertTrue(
            (subject, RDF.type, O.Text) in graph)
        self.assertTrue(
            (subject, RDF.type, O.TitleText) in graph)

    def test_sentence_length(self):
        doctree = load_doctree('text')
        parser = Doctree2RDF(doctree)
        D = parser.document_namespace

        graph = parser.get_graph()
        graph += doctree2rdf.get_ontology()
        owlrl(graph)

        subject = D.E1_1_2

        self.assertTrue(
            (subject, RDF.type, O.Paragraph) in graph)

        self.assertTrue(
            (subject, O.hasTextLength, Literal(59)) in graph)

        result = list(graph.triples((subject, O.hasFleschReadingEase, None)))
        self.assertEqual(len(result), 1)
        __, __, score_E1_1_2 = result[0]

        subject = D.E1_1_3

        self.assertTrue(
            (subject, RDF.type, O.Paragraph) in graph)

        # The text length for a paragraph includes the newlines but do not
        # include control characters like *italic*.
        self.assertTrue(
            (subject, O.hasTextLength, Literal(1305)) in graph)

        result = list(graph.triples((subject, O.hasFleschReadingEase, None)))
        self.assertEqual(len(result), 1)
        __, __, score_E1_1_3 = result[0]

        print score_E1_1_2, score_E1_1_3
