from ... import Check, Hint, Metric, metrics
from ..metrics.textstats import TextStats


__all__ = ('HasNoLongSections',)


@metrics.require(TextStats)
class SectionWordCount(Metric):
    def limit(self, nodeset):
        return nodeset.filter(type='section')

    def apply(self, node, document):
        # TODO: Querying does not work reliably yet. It counts words for
        # subsections as well I think.

        nodeset = node.nodeset.filter(word_count__exists=True)
        for textnode in nodeset:
            textnode.annotate(Hint('Words: {}'.format(textnode['word_count'])))
        word_counts = nodeset.values_list('word_count', flat=True)
        node['section_word_count'] = sum(word_counts)


@metrics.require(SectionWordCount)
class HasNoLongSections(Check):

    # 1000 words are about the number of words that fit on two printed book
    # pages. After that we should split up the section if possible.
    threshold = 1100

    message = Hint(
        'This section is quite long, it contains about {rough_word_count} '
        'words. Consider splitting it up into multiple sections.')

    def limit(self, nodeset):
        return nodeset.filter(type='section')

    def check(self, nodeset, document):
        for section in nodeset.filter(section_word_count__gt=300):
            title = section.nodeset.filter(type='title').first()
            if title:
                rough_word_count = section['section_word_count']
                rough_word_count = round(rough_word_count, -2)
                title.annotate(
                    self.message.format(
                        rough_word_count=rough_word_count))
