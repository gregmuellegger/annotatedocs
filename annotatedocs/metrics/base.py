__all__ = ('require', 'MetricRequirementMixin', 'Metric')


class MetricRequirementMixin(object):
    '''
    This mixin can be used for all classes that can require some metrics.
    Just drop it into the inheritance list and set the ``required_metrics``
    class attribute.

    Make sure to include the parents ``required_metrics`` attribute as well if
    you don't want to overwrite it::

        class MyPageType(BasicPage):
            required_metrics = BasicPage.required_metrics + [
                SpecialMetric,
                ComplexMetric,
            ]

    You can either give metric classes or instances of metric classes. Giving
    metric classes is prefered since we check for the object ID to see if we
    already have applied this metric yet. So if you give the same metric as two
    different instances, it will be applied twice.

    Unfortunatelly the ``required_metrics`` attribute cannot be altered in the
    instance of classes. Actually it can be altered, but won't have any effect.
    The reason is that the ``get_required_metrics`` method is implemented as a
    classmethod which only has access to the **class** attributes, not to the
    ones of the instance.

    It is required for implementation reasons, since we need to be able to call
    this method on all other metrics defined in ``required_metrics`` to get a
    list of all dependencies.
    '''

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


def require(*metrics):
    """
    Usage:

        from annotatedocs import metrics, Check

        @metrics.require(metrics.NodeType)
        class MyCheck(Check):
            ...

    Or:

        from annotatedocs import metrics, Check

        class MyCheck(Check):
            @metrics.require(metrics.NodeType)
            def check(self, nodeset, document):
                ...

    Is equivalent to:

        from annotatedocs import metrics, Check

        class MyCheck(Check):
            required_metrics = Check.required_metrics + [
                metrics.NodeType
            ]
    """
    def decorator(decorated):
        # If it's a class.
        if isinstance(decorated, type):
            decorated_class = decorated
        # If it's a method.
        elif hasattr(decorated, 'im_class'):
            decorated_class = decorated.im_class
        else:
            raise TypeError(
                "require() can only be applied to classes and instance "
                "methods.")
            decorated_class.required_metrics = (
                list(decorated_class.required_metrics) +
                list(metrics))
        return decorated
    return decorator


class Metric(MetricRequirementMixin, object):
    def limit(self, nodeset):
        '''
        Subclasses can limit down the nodeset they want to be applied against.
        This is usefull for metrics that does not make sense for every node.
        '''
        return nodeset.all()

    def apply_to_document(self, document):
        nodeset = document.nodeset
        for node in self.limit(nodeset):
            self.apply(node, document)

    def apply(self, node, document):
        raise NotImplementedError('Needs to be implemented by subclass.')
