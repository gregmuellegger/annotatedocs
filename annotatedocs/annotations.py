class Annotation(object):
    level = None

    def __init__(self, message, level=None):
        self.message = message
        self.level = level or self.level

    def serialize(self):
        return {
            'message': self.message,
            'level': self.level,
        }


class Hint(Annotation):
    level = 'hint'


class Warning(Annotation):
    level = 'warning'
