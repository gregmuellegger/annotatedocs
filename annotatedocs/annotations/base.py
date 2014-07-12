from ..metrics import MetricRequirementMixin


__all__ = ('Annotation',)


class Annotation(MetricRequirementMixin, object):
    '''
    Annotations are quite simple classes but fulfill a core part of the
    ``annotatedocs`` framework.

    An annotation is responsible for actually adding the messages to the
    relevant nodes.
    '''

    message = None

    def limit(self, nodeset):
        '''
        Subclassed annotations can limit down the nodeset to the nodes they
        want to apply to.
        '''
        return nodeset.all()

    def apply(self, nodeset, document):
        '''
        If the annotation only attaches a simple message to all of the limited
        nodesets nodes, then you can just set the ``message`` class attribute.

        Otherwise overwrite the ``apply()`` method and customize the message
        generation at will.
        '''
        if self.message is not None:
            for node in nodeset:
                message = self.message.format(
                    node=node,
                    annotation=self)
                node.annotate(message)
