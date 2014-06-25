import json

from rdflib import Graph, Namespace
import sphinx_rtd_theme_annotated
from sphinx.application import Sphinx
from sphinx.writers.html import HTMLTranslator
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.console import darkgreen

from . import doctree2rdf, reasoner
from .doctree2rdf import O
from .doctree2rdf import NodeIDMixin


class AnnotatedHTMLTranslator(NodeIDMixin, HTMLTranslator):
    def __init__(self, builder, document):
        NodeIDMixin.__init__(self)
        HTMLTranslator.__init__(self, builder, document)

        # If the document was not passed to the builder with a name, means that
        # it was rendered via ``StandaloneHTMLBuilder.render_partial``.
        docname = builder.docnames_by_doctree.get(document, None)
        if docname:
            self.annotate = True
            namespace_name = builder.get_namespace_name(docname)
            self.element_namespace = Namespace(namespace_name)
            self.annotation_graph = builder.annotation_graph
        else:
            self.annotate = False

    def get_value(self, node, prop):
        uri = self.get_uri(node)
        result = list(self.annotation_graph.triples((
            uri,
            prop,
            None)))
        if not result:
            return None
        return result[0][2]

    def get_annotations(self, node):
        fleschreadingease = self.get_value(node, O.hasFleschReadingEase)
        annotations = []
        if fleschreadingease is not None:
            annotations.append({
                'type': 'fleschreadingease',
                'data': {
                    'score': fleschreadingease,
                },
                'message': 'fleschreadingease: {}'.format(fleschreadingease)
            })
        return annotations

    def starttag(self, node, tagname, suffix='\n', empty=False, **attributes):
        if self.annotate:
            annotations = self.get_annotations(node)
            if annotations:
                attributes['data-annotations'] = json.dumps(annotations)
        return HTMLTranslator.starttag(self, node, tagname, suffix=suffix, empty=empty, **attributes)


class AnnotatedHTMLBuilder(StandaloneHTMLBuilder):
    allow_parallel = False

    def init_translator_class(self):
        self.translator_class = AnnotatedHTMLTranslator

    def _write_serial(self, docnames, warnings):
        doctrees_by_docname = {}
        for docname in self.status_iterator(
                docnames, 'gathering annotation data... ', darkgreen, len(docnames)):
            doctree = self.env.get_and_resolve_doctree(docname, self)
            doctrees_by_docname[docname] = doctree
        self.prepare_annotation_data(doctrees_by_docname)
        for docname in self.status_iterator(
                docnames, 'writing output... ', darkgreen, len(docnames)):
            doctree = doctrees_by_docname[docname]
            self.write_doc_serialized(docname, doctree)
            self.write_doc(docname, doctree)
        for warning in warnings:
            self.warn(*warning)

    def get_namespace_name(self, docname):
        return 'document://{0}#'.format(docname)

    def prepare_annotation_data(self, doctrees_by_docname):
        self.doctrees_by_docname = doctrees_by_docname
        self.docnames_by_doctree = dict((doctree, docname) for docname, doctree in doctrees_by_docname.items())
        graph = Graph()
        for docname, doctree in self.doctrees_by_docname.items():
            namespace_name = self.get_namespace_name(docname)
            parser = doctree2rdf.Doctree2RDF(doctree, namespace_name)
            graph += parser.get_graph()
        graph += doctree2rdf.get_ontology()
        self.info('Apply OWL reasoning on annotation data...')
#        reasoner.owlrl(graph)
        with open('/tmp/annotatedocs.ttl', 'w') as f:
            graph.serialize(f, format='turtle')
        self.annotation_graph = graph


class AnnotatedSphinx(Sphinx):
    def __init__(self, *args, **kwargs):
        confoverrides = kwargs.pop('confoverrides', {})
        confoverrides['html_theme'] = 'sphinx_rtd_theme_annotated'
        confoverrides['html_theme_path'] = [sphinx_rtd_theme_annotated.get_html_theme_path()]
        kwargs['confoverrides'] = confoverrides
        super(AnnotatedSphinx, self).__init__(*args, **kwargs)
        self.builder = AnnotatedHTMLBuilder(self)
        self.document_graphs = {}

    def get_document_graph(self, node):
        document = node
        while document.parent is not None:
            document = document.parent
        if document not in self.document_graphs:
            graph = doctree2rdf.get_graph(document, reason=False)
            self.document_graphs[document] = graph
        return self.document_graphs[document]
