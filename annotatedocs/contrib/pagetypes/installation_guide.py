from __future__ import division

from ... import Check, PageType, metrics
from ..metrics.stemmer import Stemmer


__all__ = ('InstallationGuide',)


class HasNextLink(Check):
    """
    Make sure that the page has a 'what comes next' section with a link to
    another internal document.
    """


class HasRequirements(Check):
    """
    Make sure the installation guide has a section about the requirements for
    this project.
    """


class LinkToRequirements(Check):
    """
    If the page has a section about requirements, make sure that it contains
    links to external sources (the requirements homepages).
    """


@metrics.require(Stemmer)
class InstallationGuide(PageType):
    name = 'installation guide'

    required_words = [
        'Installation',
        'pip',
        'apt-get',
    ]

    def match(self, document):
        stemmer = Stemmer()
        words = set(stemmer.stem(' '.join(self.required_words)))
        found_words = set()

        nodeset = document.nodeset.all()
        for word in words:
            if nodeset.filter(stemmed_words__contains=word).exists():
                found_words.add(word)

        found_words_ratio = len(found_words) / len(words)

        return found_words_ratio
