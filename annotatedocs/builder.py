import json

import sphinx_rtd_theme
from sphinx.application import Sphinx
from sphinx.writers.html import HTMLTranslator
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.console import darkgreen

from . import bundles
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
            self._document_annotations_set = False
        else:
            self.annotate = False

    def apply_annotation_attribute(self, attributes, attribute, annotations):
        if annotations:
            json_data = json.dumps([
                annotation.serialize()
                for annotation in annotations])
            attributes[attribute] = json_data

    def has_set_document_annotations(self):
        return self._document_annotations_set

    def set_document_annotations(self, attributes):
        """
        Set the document annotations to the given node.
        """
        self.apply_annotation_attribute(
            attributes,
            'data-global-annotations',
            self.document_structure.get_global_annotations())

        self.apply_annotation_attribute(
            attributes,
            'data-document-annotations',
            self.document_data.get_document_annotations())

        self._document_annotations_set = True

    def apply_checks(self, node):
        attributes = {}

        if not self.has_set_document_annotations():
            self.set_document_annotations(attributes)

        self.apply_annotation_attribute(
            attributes,
            'data-annotations',
            self.document_data[node].annotations)

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
            self.app.bundle_override)

        if bundle_conf is None:
            bundle = bundles.noop

        elif isinstance(bundle_conf, basestring):
            path_bits = bundle_conf.split('.')
            bundle_name = str(path_bits.pop(-1))
            module_name = '.'.join(path_bits)
            bundle_module = __import__(module_name, globals(), locals(),
                                       fromlist=[bundle_name])
            try:
                bundle = getattr(bundle_module, bundle_name)
            except AttributeError:
                raise TypeError(
                    'The given bundle {0} cannot be '
                    'imported.'.format(repr(bundle_conf)))
        else:
            bundle = bundle_conf

        # Sanity check.
        if not isinstance(bundle, bundles.Bundle):
            raise TypeError(
                'The given bundle {0} is not a subclass of '
                'Bundle.'.format(repr(bundle_conf)))
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

    def get_doc_context(self, docname, body, metatags):
        context = super(AnnotatedHTMLBuilder, self).get_doc_context(docname, body, metatags)
        document = self.document_structure.documents[docname]
        context['document_structure'] = self.document_structure
        context['document'] = document
        context['page_types'] = document.page_types
        context['checks'] = document.applied_checks
        return context


class AnnotatedSphinx(Sphinx):
    def __init__(self, *args, **kwargs):
        confoverrides = kwargs.pop('confoverrides', {})
        self.bundle_override = confoverrides.get('annotatedocs_bundle', None)

        # TODO: We force the 'annotatedocs' theme here. We should change the
        # theme so that all other themes are supported.
        confoverrides['html_theme'] = 'annotatedocs'
        confoverrides['html_theme_path'] = [sphinx_rtd_theme.get_html_theme_path()]

        kwargs['confoverrides'] = confoverrides
        super(AnnotatedSphinx, self).__init__(*args, **kwargs)

        self.builder = AnnotatedHTMLBuilder(self)
