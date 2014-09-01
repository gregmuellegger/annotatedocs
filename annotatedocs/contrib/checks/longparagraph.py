from ... import Check, Hint, metrics
from ..metrics import WordStats


__all__ = ('LongParagraph',)


@metrics.require(WordStats)
class LongParagraph(Check):
    threshold = 10
    threshold_string = 'ten'
    message = Hint(
        'This paragraph contains more than {check.threshold_string} '
        'sentences. Consider to split this paragraph into multiple '
        'paragraphs.')

    def limit(self, nodeset):
        return nodeset.filter(sentence_count__gt=self.threshold)
