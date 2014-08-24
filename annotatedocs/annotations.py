from copy import copy


__all__ = ('Annotation', 'Hint', 'Warning')


class Annotation(object):
    title_text = None
    level = None

    def __init__(self, message, level=None, title_text=None, format_args=None,
                 format_kwargs=None):
        self.message = message
        self.level = level or self.level
        self.title_text = title_text or self.title_text
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
        duplicate = copy(self)
        duplicate.format_args = format_args
        duplicate.format_kwargs = format_kwargs
        return duplicate

    def get_message(self):
        return self.message.format(
            *self.format_args,
            **self.format_kwargs)

    def serialize(self):
        data = {
            'message': self.get_message(),
            'level': self.level,
        }
        if self.title_text:
            data['title'] = self.title_text
        return data


class Hint(Annotation):
    level = 'hint'


class Warning(Annotation):
    level = 'warning'
