__all__ = ('Metric',)


class Metric(object):
    required_metrics = []

    def __init__(self):
        self.required_metrics = list(self.required_metrics)

    def get_required_metrics(self):
        return self.required_metrics

    @property
    def data(self):
        return self.document.node_data

    def limit(self, nodeset):
        '''
        Subclasses can limit down the nodeset they want to be applied against.
        This is usefull for metrics that does not make sense for every node.
        '''
        return nodeset

    def apply(self, node, document):
        raise NotImplementedError('Needs to be implemented by subclass.')
