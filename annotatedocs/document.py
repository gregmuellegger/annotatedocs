from logbook import Logger

from .nodeset import NodeSet
from .utils import instantiate


log = Logger(__name__)


NO_DEFAULT = object()


def walk(node, func):
    func(node)
    for child in node.children:
        walk(child, func)


class DocumentStructure(object):
    '''
    This is the document structure as given by the documentation project.

    It holds the ``documents`` attribute which is dictionary with the name
    of documents as key and a ``Document`` instance as value.

    The ``Document`` instances will usually hold a reference to the structure.
    This allows traversing the whole document structure in order to attach
    annotations to related documents.
    '''

    def __init__(self, documents, bundle):
        self.bundle = bundle
        self.global_annotations = []
        self.documents = {}
        if documents:
            for name, document in documents.items():
                self.add_document(name, document)

    def add_document(self, name, node):
        self.documents[name] = Document(node, self.bundle, name,
                                            structure=self)

    def get_document(self, name):
        return self.documents[name]

    def get_global_annotations(self):
        return self.global_annotations

    def analyze(self):
        for name, document in self.documents.items():
            document.analyze()

    def annotate(self, annotation):
        self.global_annotations.append(annotation)


class Document(object):
    '''
    A thin wrapper around the docutils document object. It holds data such as
    the categorisation of a document etc.

    Usually there is the ``structure`` argument given to the constructor which
    is a reference to the surrounding environment so that documents can relate
    themselves to each other. However the argument is not required. This makes
    it possible to analyze single nodes that do not exist within a bigger
    context.

    Attributes:

    ``page_types``
        A list of page type classes that the bundle has determined for this
        document. It will be ``None`` if the analyzation wasn't triggered yet.

    ``is_analyzed``
        Is set to ``True`` after the analyzation is completed.
    '''

    nodeset_class = NodeSet

    def __init__(self, node, bundle, name=None, structure=None):
        """
        Parameters
        ----------
        node : docutils.node.Node
        bundle : annotatedocs.bundle.Bundle
        name : str, optional
            The filename of the source document without the file suffix. So
            `name` will be ``contribution/license`` if the source document was
            ``contribution/license.rst``.
        structure : `DocumentStructure`, optional
        """
        self.node = node
        self.bundle = bundle
        self.name = name
        self.structure = structure

        self.data = DocumentData(self.node, document=self)

        # Data that is set during analyzing phase.
        self.page_types = None
        self.is_analyzed = False
        self.applied_metrics = set()
        self.applied_checks = set()

    def __repr__(self):
        return '<{class_name}: {name}>'.format(
            class_name=self.__class__.__name__,
            name=self.name)

    def __unicode__(self):
        return self.name

    @property
    def nodeset(self):
        """
        Returns
        -------
        NodeSet
        """
        return self.nodeset_class([self[self.node]])

    def __getitem__(self, node):
        return self.data[node]

    def apply_metric(self, metric):
        # TODO: Move this into the metric so that it can decide itself if it
        # want's to be applied multiple times or not.
        if metric in self.applied_metrics:
            return

        # Finally apply metric.
        metric_instance = instantiate(metric)
        metric_instance.apply_to_document(self)
        self.applied_metrics.add(metric)

    def apply_metrics(self, metrics):
        for metric in metrics:
            self.apply_metric(metric)

    def analyze(self):
        self.page_types = self.bundle.determine_page_types(document=self)
        for page_type in self.page_types:
            page_type.apply_checks(document=self)
        self.is_analyzed = True

    def annotate(self, *args, **kwargs):
        """
        Add annotation to ``document`` node. Use this method to add document
        wide annotations.
        """
        self[self.node].annotate(*args, **kwargs)

    def get_document_annotations(self):
        return self[self.node].annotations



class NodeData(dict):
    def __init__(self, node, document_data):
        self.node = node
        self.document_data = document_data

    def __repr__(self):
        return '<{class_name}: {node_type}>'.format(
            class_name=self.__class__.__name__,
            node_type=self.node.__class__.__name__)

    def append(self, key, value):
        self.setdefault(key, []).append(value)

    def annotate(self, message):
        self.append('annotations', message)

    @property
    def annotations(self):
        return self.get('annotations', [])

    @property
    def children(self):
        document = self.document_data.document
        return [document[child] for child in self.node.children]

    def __eq__(self, other):
        if self.node is None:
            return self is other
        return self.node is getattr(other, 'node', None)

    @property
    def nodeset(self):
        return NodeSet([self])

    @property
    def attributes(self):
        """
        Return an empty dict if the ``attributes`` attribute is not available
        on this node. This is the case for Text nodes for example.
        """
        return getattr(self.node, 'attributes', {})

    @property
    def class_name(self):
        return self.node.__class__.__name__

    @property
    def parent(self):
        """
        Return the `NodeData` instance for the parent of the docutils node.
        """
        if self.node.parent:
            return self.document_data[self.node.parent]
        else:
            return None

    # Alias methods that pass the calls through to the docutils node instance.

    def astext(self):
        return self.node.astext()


class DocumentData(object):
    '''
    A ``DocumentData`` holds the relevant data for the node and it's subtree.

    The data contains the calculated metrics as well as the generated
    annotations.
    '''

    node_data_class = NodeData

    def __init__(self, node, document=None):
        self.document = document
        self.root_node = node
        self._data = {}

    def _init_node(self, node):
        self._data[node] = self.node_data_class(node, document_data=self)

    def __getitem__(self, node):
        try:
            return self._data[node]
        except KeyError:
            self._init_node(node)
            return self._data[node]

    def get(self, node, key, default=NO_DEFAULT):
        '''
        Return the value for given node and key. If ``default`` is set, it will
        be returned if no the key was not yet set for the node.

        It will always raise an error when the node does not exist.
        '''
        data = self[node]
        if default is not NO_DEFAULT:
            return data.get(key, default)
        if key not in data:
            raise KeyError('No such key `{key}` for node `{node}`'.format(
                key=key,
                node=node))
        return data[key]
