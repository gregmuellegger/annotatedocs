from ..annotations import Hint, Warning


__all__ = ('Category',)


class Category(object):
    required_metrics = []

    def __init__(self):
        self.required_metrics = list(self.required_metrics)

    def get_required_metrics(self):
        return self.required_metrics

    def match(self, document):
        '''
        Returns a value between 0 and 1 on how good this category matches.
        '''
        return 1

    def make_annotations(self, document):
        for node in document.nodeset.all():
            if 'stemmed_words' in document[node]:
                print "Has stemmed words:", document[node]['stemmed_words']
        nodeset = document.nodeset.filter(type='paragraph')
        nodeset.annotate(Warning('This is a paragraph'))
