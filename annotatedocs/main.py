import sys


def annotate(project):
    graph = project.get_graph()
    graph.serialize(sys.stdout, format='turtle')
