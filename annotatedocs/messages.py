__all__ = ('Message', 'Hint', 'Warning')


class Message(object):
    level = None

    def __init__(self, message, level=None, format_args=None, format_kwargs=None):
        self.message = message
        self.level = level or self.level
        self.format_args = format_args or []
        self.format_kwargs = format_kwargs or {}

    def __unicode__(self):
        return unicode(self.get_message())

    def format(self, *args, **kwargs):
        '''
        This is way to emulate a unicode object, somehow.
        We remember the actual format arguments and use it when
        ``get_message()`` is called.
        '''
        format_args = list(self.format_args) + list(args)
        format_kwargs = self.format_kwargs.copy()
        format_kwargs.update(kwargs)
        return self.__class__(self.message, self.level,
                              format_args, format_kwargs)

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
