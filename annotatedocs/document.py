from logbook import Logger
from .nodeset import NodeSet
from .bundle import Bundle
from .page_types import DefaultPage, InstallationGuide


log = Logger(__name__)


NO_DEFAULT = object()


def walk(node, func):
    func(node)
    for child in node.children:
        walk(child, func)


default_bundle = Bundle(
    InstallationGuide,
    default_page_type=DefaultPage,
)


class DocumentStructure(object):
    '''
    This is the document structure as given by the documentation project.

    It holds the ``document_data`` attribute which is dictionary with the name
    of documents as key and a ``Document`` instance as value.

    The ``Document`` instances will usually hold a reference to the structure.
    This allows traversing the whole document structure in order to related
    annotations to other documents.
    '''

    def __init__(self, documents, bundle):
        self.bundle = bundle
        self.global_annotations = []
        self.document_data = {}
        if documents:
            for name, document in documents.items():
                self.add_document(name, document)

    def add_document(self, name, node):
        self.document_data[name] = Document(node, self.bundle, name,
                                            structure=self)

    def get_document(self, name):
        return self.document_data[name]

    def get_global_annotations(self):
        from .annotations import Warning
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

    def __init__(self, node, bundle, name=None, structure=None):
        self.node = node
        self.bundle = bundle
        self.name = name
        self.structure = structure

        self.data = DocumentData(self.node, document=self)

        # Data that is set during analyzing phase.
        self.page_type = None
        self.is_analyzed = False
        self.applied_metrics = set()

    @property
    def nodeset(self):
        return self.nodeset_class(self)

    def __getitem__(self, node):
        return self.data[node]

    def get_required_metrics(self):
        metrics = set()
        for page_type in self.bundle.get_page_types():
            metrics.update(
                page_type.get_required_metrics())
        return metrics

    def apply_metric(self, metric_class):
        if metric_class in self.applied_metrics:
            return

        # Finally apply metric.
        metric = metric_class()
        nodeset = self.nodeset.all()
        nodeset = metric.limit(nodeset)
        for node in nodeset:
            metric.apply(node)

        self.applied_metrics.add(metric_class)

    def apply_metrics(self, metric_classes):
        for metric_class in metric_classes:
            self.apply_metric(metric_class)

    def determine_page_type(self):
        # TODO: Check if this method is better suited in the Bundle class.
        matched_page_types = []
        for page_type_class in self.bundle.get_page_types():
            page_type = page_type_class()
            match = page_type.match(document=self)
            matched_page_types.append((match, page_type))
        matched_page_types = sorted(matched_page_types, key=lambda mc: mc[0])

        # TODO: check if there are multiple page types with the same match
        # value.
        match, best_page_type = matched_page_types[0]

        # We have no matched page type. So we return the default page type.
        if match < self.bundle.minimum_page_type_match:
            default_page_type_class = self.bundle.get_default_page_type()
            if default_page_type_class is None:
                raise TypeError(
                    u'The given bundle does not provide a default page type..')

            default_page_type = default_page_type_class()

            # We have not applied the default page types' metrics so far. So
            # let's do that. We want to be equal to all page types, don't we?
            self.apply_metrics(default_page_type.get_required_metrics())

            # And therefore we also need to call the match method.
            default_page_type.match(document=self)

            return default_page_type
        return best_page_type

    def analyze(self):
        self.apply_metrics(self.get_required_metrics())
        self.page_type = self.determine_page_type()
        self.page_type.apply_annotations(self)
        self.is_analyzed = True


class NodeData(dict):
    def __init__(self, node, document_data):
        self.node = node
        self.document_data = document_data

    def append(self, key, value):
        self.setdefault(key, []).append(value)

    def annotate(self, message):
        self.append('messages', message)

    @property
    def messages(self):
        return self.get('messages', [])


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
