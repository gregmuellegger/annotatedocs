# -*- coding: utf-8 -*-
import os
import requests
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
#
#    graph += get_inferred(graph)
#    return

    from RDFClosure.OWLRLExtras import OWLRL_Extension_Trimming
    from RDFClosure import DeductiveClosure, return_closure_class

    closure = DeductiveClosure(
        return_closure_class(
            owl_closure=True,
            rdfs_closure=True,
            owl_extras=False,
            trimming=True),
        improved_datatypes=True,
        rdfs_closure=True,
        axiomatic_triples=False,
        datatype_axioms=False)

    closure.expand(graph)


def get_inferred(graph):
    buf = StringIO()
    data = graph.serialize(buf, format='turtle')
    response = requests.post(
        'http://localhost:8080/damuellegger/rest/enrichrdf/infer',
        data=data)
    assert response.status_code == 200
    buf = StringIO(response.content)
    inferred = Graph()
    inferred.parse(buf, format='turtle')
    return inferred
