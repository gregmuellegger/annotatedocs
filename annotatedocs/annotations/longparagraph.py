from .base import Annotation, Hint
from ..metrics import WordStats


__all__ = ('LongParagraph',)


class LongParagraph(Annotation):
    required_metrics = [
        WordStats,
    ]

    threshold = 10
    threshold_string = 'ten'
    message = Hint(
        'This paragraph contains more than {annotation.threshold_string} '
        'sentences.')

    def limit(self, nodeset):
        return nodeset.filter(sentence_count__gt=self.threshold)
