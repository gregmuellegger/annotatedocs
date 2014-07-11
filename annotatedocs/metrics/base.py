__all__ = ('MetricRequirementMixin', 'Metric')


class MetricRequirementMixin(object):
    required_metrics = []

    @classmethod
    def get_required_metrics(cls):
        '''
        Resolve all dependencies and bring them in the correct order.

        Requirements that should be applied first will be returned first.
        '''

        # TODO: Check for circular dependencies.
        dependencies = []
        class_metrics = list(cls.required_metrics)
        for required in class_metrics:
            for dependency in required.get_required_metrics():
                if dependency in dependencies:
                    continue
                dependencies.append(dependency)
        return dependencies + class_metrics


class Metric(MetricRequirementMixin, object):
    @property
    def data(self):
        return self.document.node_data

    def limit(self, nodeset):
        '''
        Subclasses can limit down the nodeset they want to be applied against.
        This is usefull for metrics that does not make sense for every node.
        '''
        return nodeset.all()

    def apply(self, node, document):
        raise NotImplementedError('Needs to be implemented by subclass.')
