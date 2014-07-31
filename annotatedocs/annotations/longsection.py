from . import Annotation, Hint
from ..metrics import Metric, WordStats


__all__ = ('LongSection',)


class SectionWordCount(Metric):
    required_metrics = Metric.required_metrics + [
        WordStats,
    ]

    def limit(self, nodeset):
        return nodeset.filter(type='section')

    def apply(self, node):
        # TODO: Querying does not work reliably yet. It counts words for
        # subsections as well I think.

        nodeset = node.nodeset.filter(word_count__exists=True)
        for textnode in nodeset:
            textnode.annotate(Hint('Words: {}'.format(textnode['word_count'])))
        word_counts = nodeset.values_list('word_count', flat=True)
        node['section_word_count'] = sum(word_counts)


class LongSection(Annotation):

    # 1000 words are about the number of words that fit on two printed book
    # pages. After that we should split up the section if possible.
    threshold = 1100

    required_metrics = Annotation.required_metrics + [
        SectionWordCount,
    ]

    message = Hint(
        'This section is quite long, it contains about {rough_word_count} '
        'words. Consider splitting it up into multiple sections.')

    def limit(self, nodeset):
        return nodeset.filter(type='section')

    def apply(self, nodeset, document):
        for section in nodeset.filter(section_word_count__gt=300):
            title = section.nodeset.filter(type='headline').first()
            if title:
                rough_word_count = section['section_word_count']
                rough_word_count = round(rough_word_count, -2)
                title.annotate(
                    self.message.format(
                        rough_word_count=rough_word_count))
