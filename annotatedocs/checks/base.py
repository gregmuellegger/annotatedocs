from ..metrics import MetricRequirementMixin


__all__ = ('Check',)


class Check(MetricRequirementMixin, object):
    """
    Checks are quite simple classes but fulfill a core part of the
    annotatedocs framework.

    A check is responsible for actually adding the annotations to the relevant
    nodes.
    """

    message = None

    def limit(self, nodeset):
        '''
        Subclassed checks can limit down the nodeset to the nodes they want to
        apply to.
        '''
        return nodeset.all()

    def check(self, nodeset, document):
        """
        If the check only attaches a simple annotation to all of the limited
        nodesets nodes, then you can just set the `self.annotation` class
        attribute.

        Otherwise overwrite the ``check()`` method and customize it at your
        will.
        """
        if self.annotation is not None:
            for node in nodeset:
                annotation = self.annotation.format(
                    node=node,
                    check=self)
                node.annotate(annotation)
