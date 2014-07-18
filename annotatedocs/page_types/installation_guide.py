from __future__ import division

from .base import BasicPage
from ..metrics import Stemmer


__all__ = ('InstallationGuide',)


class InstallationGuide(BasicPage):
    name = 'installation guide'

    required_metrics = BasicPage.required_metrics + [
        Stemmer,
    ]

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
