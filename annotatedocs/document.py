from logbook import Logger
from .nodeset import NodeSet
from .categories import InstallationGuide


log = Logger(__name__)


NO_DEFAULT = object()


CATEGORIES = [
    InstallationGuide,
]


def walk(node, func):
    func(node)
    for child in node.children:
        walk(child, func)


class Annotation(object):
    level = None

    def __init__(self, message, level=None):
        self.message = message
        self.level = level or self.level

    def serialize(self):
        return {
            'message': self.message,
            'level': self.level,
        }


class Hint(Annotation):
    level = 'hint'


class Warning(Annotation):
    level = 'warning'


class DocumentStructure(object):
    '''
    This is the document structure as given by the documentation project.

    It holds the ``document_data`` attribute which is dictionary with the name
    of documents as key and a ``NodeData`` instance as value.
    '''

    def __init__(self, documents=None):
        self.global_annotations = []
        self.document_data = {}
        if documents:
            for name, document in documents.items():
                self.add_document(name, document)

    def add_document(self, name, node):
        self.document_data[name] = Document(node, name, structure=self)

    def get_document(self, name):
        return self.document_data[name]

    def get_global_annotations(self):
        return [Warning('This is a global warning')]

    def analyze(self):
        for name, document_data in self.document_data.items():
            document_data.analyze()


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

    ``is_analyzed``
        Is set to ``True`` after the analyzation is completed.
    '''

    nodeset_class = NodeSet

    def __init__(self, node, name=None, structure=None):
        self.node = node
        self.name = name
        self.structure = structure

        self.data = NodeData(self.node, document=self)

        # Data that is set during analyzing phase.
        self.category = None
        self.is_analyzed = False
        self.applied_metrics = set()

        self.possible_categories = [
            category()
            for category in CATEGORIES]

    def get_required_metrics(self):
        metrics = set()
        for category in self.possible_categories:
            metrics.update(
                category.get_required_metrics())
        return metrics

    def apply_metrics(self):
        for metric_class in self.get_required_metrics():
            metric = metric_class()
            nodeset = self.nodeset.all()
            nodeset = metric.limit(nodeset)
            for node in nodeset:
                metric.apply(
                    node=node,
                    data=self[node])
            self.applied_metrics.add(metric_class)

    def analyze(self):
        self.apply_metrics()
        self.category = self.determine_category()
        self.category.make_annotations(self)
        self.is_analyzed = True

    def determine_category(self):
        matched_categories = []
        for category in self.possible_categories:
            match = category.match(document=self)
            matched_categories.append((match, category))
        matched_categories = sorted(matched_categories, key=lambda mc: mc[0])
        return matched_categories[0][1]

    def get_annotations(self, node):
        return self.data.get(node, 'annotations', [])

    def add_annotation(self, node, annotation):
        self.data.add_annotation(node, annotation)

    @property
    def nodeset(self):
        return self.nodeset_class(self)

    def __getitem__(self, node):
        return self.data[node]


class DataItem(dict):
    def __init__(self, node_data):
        self.node_data = node_data

    def append(self, key, value):
        self.setdefault(key, []).append(value)


class NodeData(object):
    '''
    A ``NodeData`` holds the relevant data for the node and it's subtree.

    The data contains the calculated metrics as well as the generated
    annotations.
    '''

    data_item_class = DataItem

    def __init__(self, node, document=None):
        self.document = document
        self.root_node = node
        self._init_data()

    def _init_data(self):
        self._data = {}

        def init_node(node):
            self._data[node] = self.data_item_class(self)

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

    def add_annotation(self, node, annotation):
        data = self._data[node]
        data.setdefault('annotations', []).append(annotation)
