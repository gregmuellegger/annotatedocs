from ..metrics import MetricRequirementMixin


__all__ = ('Message', 'Hint', 'Warning', 'Annotation',)


class Message(object):
    level = None

    def __init__(self, message, level=None):
        self.message = message
        self.level = level or self.level
        self.format_args = []
        self.format_kwargs = {}

    def __unicode__(self):
        return unicode(self.get_message())

    def format(self, *args, **kwargs):
        '''
        This is way to emulate a unicode object, somehow.
        We remember the actual format arguments and use it when
        ``get_message()`` is called.
        '''
        self.format_args = args
        self.format_kwargs = kwargs
        return self

    def get_message(self):
        return self.message.format(
            *self.format_args,
            **self.format_kwargs)

    def serialize(self):
        return {
            'message': self.get_message(),
            'level': self.level,
        }


class Hint(Message):
    level = 'hint'


class Warning(Message):
    level = 'warning'


class Annotation(MetricRequirementMixin, object):
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
            message = self.message.format(annotation=self)
            nodeset.annotate(message)
