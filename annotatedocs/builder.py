import json

import sphinx_rtd_theme_annotated
from sphinx.application import Sphinx
from sphinx.writers.html import HTMLTranslator
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.console import darkgreen

from .data import AnnotationData


class AnnotatedHTMLTranslator(HTMLTranslator):
    def __init__(self, builder, document):
        HTMLTranslator.__init__(self, builder, document)

        # If the document was not passed to the builder with a name, means that
        # it was rendered via ``StandaloneHTMLBuilder.render_partial``.
        docname = builder.docnames_by_doctree.get(document, None)
        if docname:
            self.annotate = True
            self.annotation_data = builder.annotation_data
        else:
            self.annotate = False

    def get_annotations(self, node):
        data = self.annotation_data[node]
        return data.get('annotations', [])

    def is_first_visible_node(self, node):
        '''
        Determine if the given node will the first rendered one in the
        document. That is the case if the parent is the document node, and the
        node is the first child of the document.
        '''
        return (
            node.parent is node.document and
            node.parent.index(node) == 0)

    def get_global_annotations(self, node):
        if self.is_first_visible_node(node):
#            return self.annotation_data.get_global_annotations()
            annotations = [{
                'level': 'warning',
                'message': 'This is a global warning'
            }]
            return annotations

    def get_document_annotations(self, node):
        if self.is_first_visible_node(node):
            return self.get_annotations(node.document)

    def apply_annotations(self, node):
        attributes = {}
        global_annotations = self.get_global_annotations(node)
        if global_annotations:
            attributes['data-global-annotations'] = json.dumps(global_annotations)

        document_annotations = self.get_document_annotations(node)
        if document_annotations:
            attributes['data-document-annotations'] = json.dumps(document_annotations)

        annotations = self.get_annotations(node)
        if annotations:
            attributes['data-annotations'] = json.dumps(annotations)
        return attributes

    def starttag(self, node, tagname, suffix='\n', empty=False, **attributes):
        if self.annotate:
            attributes.update(
                self.apply_annotations(node))
        return HTMLTranslator.starttag(self, node, tagname, suffix=suffix,
                                       empty=empty, **attributes)


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
        self.docnames_by_doctree = dict(
            (doctree, docname)
            for docname, doctree in doctrees_by_docname.items())

        self.annotation_data = AnnotationData()
        for docname, doctree in self.doctrees_by_docname.items():
            self.annotation_data.add_document(doctree, docname)


class AnnotatedSphinx(Sphinx):
    def __init__(self, *args, **kwargs):
        confoverrides = kwargs.pop('confoverrides', {})
        confoverrides['html_theme'] = 'sphinx_rtd_theme_annotated'
        confoverrides['html_theme_path'] = [sphinx_rtd_theme_annotated.get_html_theme_path()]
        kwargs['confoverrides'] = confoverrides
        super(AnnotatedSphinx, self).__init__(*args, **kwargs)
        self.builder = AnnotatedHTMLBuilder(self)
