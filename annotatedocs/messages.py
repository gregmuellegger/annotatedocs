__all__ = ('Message', 'Hint', 'Warning')


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
