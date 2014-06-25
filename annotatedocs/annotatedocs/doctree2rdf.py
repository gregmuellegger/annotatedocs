# -*- coding: utf-8 -*-
'''
Give a doctree file generated by Sphinx as argument and get a RDF
representation of the document.
'''

import logging
import os
import pickle
from docutils import nodes
from rdflib import Graph, Namespace, Literal
from rdflib import RDF, RDFS, OWL
from annotatedocs.vendored.nltk_contrib.readability.readabilitytests import ReadabilityTool
from .reasoner import owlrl


ONTOLOGY_NAMESPACE = Namespace('http://gremu.net/documentation-ontology/#')
O = ONTOLOGY_NAMESPACE


logger = logging.getLogger(__name__)


class NodeIDMixin(object):
    def __init__(self, *args, **kwargs):
        super(NodeIDMixin, self).__init__(*args, **kwargs)
        self.id_map = {}

    def get_id(self, node):
        if node not in self.id_map:
            # It must be the root element, so we assign it the ID 1.
            if node.parent is None:
                self.id_map[node] = '1'
            else:
                index = node.parent.children.index(node)
                self.id_map[node] = '{}_{}'.format(
                    self.get_id(node.parent),
                    index + 1)
        return self.id_map[node]

    def get_uri(self, node):
        if node.parent is None:
            return self.element_namespace['Document']
        node_id = self.get_id(node)
        return self.element_namespace['E{}'.format(node_id)]


class RDFVisitor(NodeIDMixin, nodes.NodeVisitor):
    '''
    Takes care of transforming a node into RDF data.

    For supported node types see the visit_* method definitions.

    Unsupported nodes will have a type of ``d:UnknownNodeType``.
    '''

    def __init__(self, document, graph, element_namespace):
        self.graph = graph
        self.node_count = 0
        self.element_namespace = element_namespace
        NodeIDMixin.__init__(self)
        nodes.NodeVisitor.__init__(self, document)

    def unknown_visit(self, node):
        self.document.reporter.info(
            'Unknown node type: {}'.format(node.__class__.__name__))
        self.add_node(node, type='UnknownNodeType')

    def add_node(self, node, type):
        subject = self.get_uri(node)

        # NODE a TYPE .
        self.graph.add((
            subject,
            RDF.type,
            O[type]
        ))

        # NODE hasParent PARENT .
        if node.parent:
            self.graph.add((
                subject,
                O.hasParent,
                self.get_uri(node.parent),
            ))

        # NODE isNodeNumber INT .
        self.node_count += 1
        self.graph.add((
            self.get_uri(node),
            O.isNodeNumber,
            Literal(self.node_count)))

        # NODE isChildNumber INT .
        if node.parent:
            child_index = node.parent.children.index(node) + 1
            self.graph.add((
                self.get_uri(node),
                O.isChildNumber,
                Literal(child_index)))

    def get_unicode(self, text):
        try:
            text = text.decode('utf-8')
        except UnicodeEncodeError:
            ascii_text = ''.join([c for c in text if ord(c) < 128])
            text = ascii_text.decode('utf-8')
        assert type(text) == unicode
        return text

    def add_text(self, node):
        # NODE rdfs:label "Text"
        text = self.get_unicode(node.astext())
        self.graph.add((
            self.get_uri(node),
            RDFS.label,
            Literal(text)
        ))

        # NODE O:hasTextLength 4
        text_length = len(text)
        self.graph.add((
            self.get_uri(node),
            O.hasTextLength,
            Literal(text_length)
        ))

        # Disable warnings emitted by ReadabilityTool.
        logging.disable(logging.WARNING)
        readability_text = ReadabilityTool()
        readability_text.lang = 'eng'
        try:
            score = readability_text.FleschReadingEase(text.encode('utf-8'))
        except ZeroDivisionError:
            score = None
        logging.disable(logging.NOTSET)

        if score is not None:
            # NODE O.hasFleschReadingEase 80.1
            self.graph.add((
                self.get_uri(node),
                O.hasFleschReadingEase,
                Literal(score)
            ))


    def _visit_node_type(type, modifier=None):
        def visit_node(self, node):
            self.add_node(node, type=type)
        return visit_node

    def _visit_list_type(type):
        def visit_node(self, node):
            self.add_node(node, type=type)
            self.graph.add((
                self.get_uri(node),
                O.hasListLength,
                Literal(len(node))
            ))
        return visit_node

    def _visit_text_type(type):
        def visit_node(self, node):
            self.add_node(node, type=type)
            self.add_text(node)
        return visit_node

    # Root element
    def visit_document(self, node):
        self.add_node(node, type='Document')

        self.graph.add((
            self.get_uri(node),
            OWL.sameAs,
            self.element_namespace['E1']
        ))

    # Title elements
    visit_title = _visit_node_type('Title')
    visit_subtitle = _visit_node_type('Subtitle')
    visit_rubric = _visit_node_type('Rubric')

    # Bibliographic elements
    visit_docinfo = _visit_node_type('Docinfo')
    visit_author = _visit_node_type('Author')
    visit_authors = _visit_node_type('Authors')
    visit_organization = _visit_node_type('Organizaion')
    visit_address = _visit_node_type('Address')
    visit_contact = _visit_node_type('Contact')
    visit_version = _visit_node_type('Version')
    visit_revision = _visit_node_type('Revision')
    visit_status = _visit_node_type('Status')
    visit_date = _visit_node_type('Date')
    visit_copyright = _visit_node_type('Copyright')

    # Decorative elements
    visit_decoration = _visit_node_type('Decoration')
    visit_header = _visit_node_type('Header')
    visit_footer = _visit_node_type('Footer')

    # Structural elements
    visit_section = _visit_node_type('Section')
    visit_topic = _visit_node_type('Topic')
    visit_sidebar = _visit_node_type('Sidebar')
    visit_transition = _visit_node_type('Transition')

    # Body elements
    visit_paragraph = _visit_text_type('Paragraph')

    visit_compound = _visit_node_type('Compound')
    visit_container = _visit_node_type('Container')
    visit_bullet_list = _visit_list_type('BulletList')
    visit_enumerated_list = _visit_list_type('EnumeratedList')
    visit_list_item = _visit_text_type('ListItem')
    visit_definition_list = _visit_list_type('DefinitionList')
    visit_definition_list_item = _visit_node_type('DefinitionListItem')
    visit_term = _visit_node_type('Term')
    visit_classifier = _visit_node_type('Classifier')
    visit_definition = _visit_node_type('Definition')
    visit_field_list = _visit_list_type('FieldList')
    visit_field = _visit_node_type('Field')
    visit_field_name = _visit_node_type('FieldName')
    visit_field_body = _visit_node_type('FieldBody')
    visit_option = _visit_node_type('Option')
    visit_option_argument = _visit_node_type('OptionArgument')
    visit_option_group = _visit_node_type('OptionGroup')
    visit_option_list = _visit_list_type('OptionList')
    visit_option_list_item = _visit_node_type('OptionListItem')
    visit_option_string = _visit_node_type('OptionString')
    visit_description = _visit_node_type('Description')
    visit_literal_block = _visit_node_type('LiteralBlock')
    visit_doctest_block = _visit_node_type('DoctestBlock')
    visit_math_block = _visit_node_type('MathBlock')
    visit_line_block = _visit_node_type('LineBlock')
    visit_line = _visit_node_type('Line')
    visit_block_quote = _visit_node_type('Blockquote')
    visit_attribution = _visit_node_type('Attribution')
    visit_attention = _visit_node_type('Attention')
    visit_caution = _visit_node_type('Caution')
    visit_danger = _visit_node_type('Danger')
    visit_error = _visit_node_type('Error')
    visit_important = _visit_node_type('Important')
    visit_note = _visit_node_type('Node')
    visit_tip = _visit_node_type('Tip')
    visit_hint = _visit_node_type('Hint')
    visit_warning = _visit_node_type('Warning')
    visit_admonition = _visit_node_type('Admonition')
    visit_comment = _visit_node_type('Comment')
    visit_substitution_definition = _visit_node_type('SubstitutionDefinition')
    visit_target = _visit_node_type('Target')
    visit_footnote = _visit_node_type('Footnode')
    visit_citation = _visit_node_type('Citation')
    visit_label = _visit_node_type('Label')
    visit_figure = _visit_node_type('Figure')
    visit_caption = _visit_node_type('Caption')
    visit_legend = _visit_node_type('Legend')
    visit_table = _visit_node_type('Table')
    visit_tgroup = _visit_node_type('TableGroup')
    visit_colspec = _visit_node_type('Colspec')
    visit_thead = _visit_node_type('TableHead')
    visit_tbody = _visit_node_type('TableBody')
    visit_row = _visit_node_type('Pending')
    visit_entry = _visit_node_type('Entry')
    visit_system_message = _visit_node_type('SystemMessage')
    visit_pending = _visit_node_type('Pending')
    visit_raw = _visit_node_type('Raw')

    # Inline elements
    visit_emphasis = _visit_node_type('Emphasis')
    visit_strong = _visit_node_type('Strong')
    visit_literal = _visit_node_type('Literal')
    visit_reference = _visit_node_type('Reference')
    visit_footnote_reference = _visit_node_type('FootnoteReference')
    visit_citation_reference = _visit_node_type('CitationReference')
    visit_substitution_reference = _visit_node_type('SubstitutionReference')
    visit_title_reference = _visit_node_type('TitleReference')
    visit_abbreviation = _visit_node_type('Abbreviation')
    visit_acronym = _visit_node_type('Acronym')
    visit_superscript = _visit_node_type('Superscript')
    visit_subscript = _visit_node_type('Subscript')
    visit_math = _visit_node_type('Math')
    visit_image = _visit_node_type('Image')
    visit_inline = _visit_node_type('Inline')
    visit_problematic = _visit_node_type('Problematic')
    visit_generated = _visit_node_type('Generated')

    # Text nodes

    def visit_Text(self, node):
        self.add_node(node, type='Text')
        self.add_text(node)

    # Clean up helpers
    del _visit_node_type
    del _visit_list_type


class Doctree2RDF(object):
    '''
    This class takes care of converting a ``docutils.nodes.document`` instance
    into a RDF graph (``rdflib.Graph``).

    Usage::

        converter = Doctree2RDF(document)
        converter.serialize(sys.stdout, format='turtle')
    '''
    visitor_class = RDFVisitor

    def __init__(self, document, document_name='document://'):
        self.document = document
        self.document_name = document_name
        self.document_namespace = Namespace(self.document_name)

    def rdf_for_node(self, node):
        return str(node.__class__)

    def rdf_for_node_recursive(self, node):
        return [self.rdf_for_node(node)] + [
            self.rdf_for_node_recursive(child)
            for child in node.children]

    def bind_namespaces(self, graph):
        graph.bind('d', ONTOLOGY_NAMESPACE)
        graph.bind('owl', OWL)

    def get_graph(self):
        '''
        Set ``raw=True`` to not include the ontology triples in
        ``doctree_rules.n3``.

        Set ``reason=True`` to apply OWL-RL reasoning on the constructed
        graph. This will include inferred triples.
        '''
        graph = Graph()
        self.bind_namespaces(graph)
        visitor = self.visitor_class(
            self.document,
            graph,
            self.document_namespace)
        self.document.walk(visitor)
        return graph

    def serialize(self, outfile, format):
        graph = self.get_graph()
        graph.serialize(outfile, format=format)


def get_ontology():
    path = os.path.join(
        os.path.dirname(__file__), 'ontologies', 'doctree_rules.n3')
    graph = Graph()
    with open(path, 'r') as file:
        graph.parse(file, format='n3')
    return graph


def get_graph(document, reason=True):
    parser = Doctree2RDF(document)
    graph = parser.get_graph()
    graph += get_ontology()
    if reason:
        owlrl(graph)
    return graph


def load(stream, init_kwargs=None):
    '''
    Get a filelike object and return a ``Doctree2RDF`` instance.
    '''
    document = pickle.load(stream)
    if not isinstance(document, nodes.document):
        raise Exception('Expected a document in file.')
    document.reporter = logger
    if init_kwargs is None:
        init_kwargs = {}
    return Doctree2RDF(document, **init_kwargs)