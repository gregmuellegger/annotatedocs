import nltk
from nltk.stem.porter import PorterStemmer

from .base import Metric


__all__ = ('Stemmer',)


class Stemmer(Metric):
    stemmer_class = PorterStemmer

    def __init__(self, *args, **kwargs):
        super(Stemmer, self).__init__(*args, **kwargs)
        self.stemmer = self.stemmer_class()

    def limit(self, nodeset):
        return nodeset.filter(type='paragraph')

    def stem(self, text):
        for sentence in nltk.sent_tokenize(text):
            for token in nltk.word_tokenize(sentence):
                stemmed_word = self.stemmer.stem(token)
                yield stemmed_word.lower()

    def apply(self, node, data):
        stemmed_words = data.setdefault('stemmed_words', set())
        text = node.astext()
        for word in self.stem(text):
            stemmed_words.add(word)