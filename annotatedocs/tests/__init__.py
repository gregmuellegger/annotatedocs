# -*- coding: utf-8 -*-
import os
from StringIO import StringIO
from rdflib import Graph


FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'fixtures')


def load_fixture(name):
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
