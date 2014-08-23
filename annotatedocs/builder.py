import json

import sphinx_rtd_theme
from sphinx.application import Sphinx
from sphinx.writers.html import HTMLTranslator
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.console import darkgreen

from .document import DocumentStructure


class AnnotatedHTMLTranslator(HTMLTranslator):
    def __init__(self, builder, document):
        HTMLTranslator.__init__(self, builder, document)

        # If the document was not passed to the builder with a name, means that
        # it was rendered via ``StandaloneHTMLBuilder.render_partial``.
        docname = builder.docnames_by_doctree.get(document, None)
        if docname:
            self.annotate = True
            self.document_structure = builder.document_structure
            self.document_data = self.document_structure.get_document(docname)
        else:
            self.annotate = False

    def is_first_visible_node(self, node):
        '''
        Determine if the given node will the first rendered one in the
        document. That is the case if the parent is the document node, and the
        node is the first child of the document.
        '''
        return (
            node.parent is node.document and
            node.parent.index(node) == 0)

    def apply_annotation_attribute(self, attributes, attribute, messages):
        if messages:
            json_data = json.dumps([
                message.serialize()
                for message in messages])
            attributes[attribute] = json_data

    def apply_checks(self, node):
        attributes = {}

        if self.is_first_visible_node(node):
            self.apply_annotation_attribute(
                attributes,
                'data-global-annotations',
                self.document_structure.get_global_annotations())

            self.apply_annotation_attribute(
                attributes,
                'data-document-annotations',
                self.document_data[node.document].messages)

        self.apply_annotation_attribute(
            attributes,
            'data-annotations',
            self.document_data[node].messages)

        return attributes

    def starttag(self, node, tagname, suffix='\n', empty=False, **attributes):
        if self.annotate:
            attributes.update(self.apply_checks(node))
        return HTMLTranslator.starttag(self, node, tagname, suffix=suffix,
                                       empty=empty, **attributes)


class AnnotatedHTMLBuilder(StandaloneHTMLBuilder):
    allow_parallel = False

    def init_translator_class(self):
        self.translator_class = AnnotatedHTMLTranslator

    def _write_serial(self, docnames, warnings):
        doctrees_by_docname = {}
        for docname in self.status_iterator(
                docnames,
                'gathering annotation data... ',
                darkgreen,
                len(docnames)):
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

    def get_bundle(self):
        # The config will only be set if 'annotatedocs' is listed as an
        # extension in the conf.py

        # TODO: Fix this by moving all the logic of this into a sphinx
        # extension.
        bundle_conf = getattr(
            self.app.config,
            'annotatedocs_bundle',
            'annotatedocs.bundles.default_bundle')

        if isinstance(bundle_conf, basestring):
            path_bits = bundle_conf.split('.')
            bundle_name = path_bits.pop(-1)
            module_name = '.'.join(path_bits)
            bundle_module = __import__(module_name, globals(), locals(),
                                       [bundle_name], -1)
            bundle = getattr(bundle_module, bundle_name)
        else:
            bundle = bundle_conf
        return bundle

    def prepare_annotation_data(self, doctrees_by_docname):
        self.doctrees_by_docname = doctrees_by_docname
        self.docnames_by_doctree = dict(
            (doctree, docname)
            for docname, doctree in doctrees_by_docname.items())

        self.document_structure = DocumentStructure(self.doctrees_by_docname,
                                                    bundle=self.get_bundle())
        # Kick off the analyzing step. This includes finding the page types and
        # checking the relevant nodes for flaws.
        self.document_structure.analyze()


class AnnotatedSphinx(Sphinx):
    def __init__(self, *args, **kwargs):
        confoverrides = kwargs.pop('confoverrides', {})

        # TODO: We force the 'annotatedocs' theme here. We should change the
        # theme so that all other themes are supported.
        confoverrides['html_theme'] = 'annotatedocs'
        confoverrides['html_theme_path'] = [sphinx_rtd_theme.get_html_theme_path()]

        kwargs['confoverrides'] = confoverrides
        super(AnnotatedSphinx, self).__init__(*args, **kwargs)

        self.builder = AnnotatedHTMLBuilder(self)
