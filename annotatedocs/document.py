from logbook import Logger
from .nodeset import NodeSet


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
        from .annotations import Warning
        return [Warning('This is a global warning')]

    def analyze(self):
        for name, document in self.documents.items():
            document.analyze()


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
        self.node = node
        self.bundle = bundle
        self.name = name
        self.structure = structure

        self.data = DocumentData(self.node, document=self)

        # Data that is set during analyzing phase.
        self.page_types = None
        self.is_analyzed = False
        self.applied_metrics = set()

    def __repr__(self):
        return '<{class_name}: {name}>'.format(
            class_name=self.__class__.__name__,
            name=self.name)

    def __unicode__(self):
        return self.name

    @property
    def nodeset(self):
        return self.nodeset_class([self[self.node]])

    def __getitem__(self, node):
        return self.data[node]

    def apply_metric(self, metric_class):
        if metric_class in self.applied_metrics:
            return

        # Finally apply metric.
        metric = metric_class()
        nodeset = self.nodeset.all()
        nodeset = metric.limit(nodeset)
        for node in nodeset:
            metric.apply(node, self)

        self.applied_metrics.add(metric_class)

    def apply_metrics(self, metric_classes):
        for metric_class in metric_classes:
            self.apply_metric(metric_class)

    def analyze(self):
        self.page_types = self.bundle.determine_page_types(document=self)
        for page_type in self.page_types:
            page_type.apply_checks(document=self)
        self.is_analyzed = True


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
        self.append('messages', message)

    @property
    def messages(self):
        return self.get('messages', [])

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
        self._init_data()

    def _init_data(self):
        self._data = {}

        def init_node(node):
            self._data[node] = self.node_data_class(node, document_data=self)

        walk(self.root_node, init_node)

    def __getitem__(self, node):
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
