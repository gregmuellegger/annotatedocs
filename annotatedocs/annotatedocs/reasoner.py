# -*- coding: utf-8 -*-
import os
from StringIO import StringIO
from rdflib import Graph


FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'fixtures')


def fixture(name):
    filename = os.path.join(FIXTURE_DIR, name)
    with file(filename, 'r') as filehandle:
        return normalize_to_graph(filehandle.read())


def normalize_to_graph(content, format='turtle'):
    if isinstance(content, Graph):
        return content
    if not hasattr(content, 'read'):
        content = StringIO(content)
    graph = Graph()
    graph.parse(content, format=format)
    return graph


def owlrl(graph):
    from RDFClosure.OWLRLExtras import OWLRL_Extension_Trimming
    from RDFClosure import DeductiveClosure

    closure = DeductiveClosure(
        OWLRL_Extension_Trimming,
        improved_datatypes=False,
        rdfs_closure=True,
        axiomatic_triples=False,
        datatype_axioms=False)

    closure.expand(graph)
