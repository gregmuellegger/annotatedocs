import nltk
from nltk.stem.porter import PorterStemmer

from .base import Metric
from .nodetype import NodeType


__all__ = ('Stemmer',)


class Stemmer(Metric):
    required_metrics = [
        NodeType,
    ]

    stemmer_class = PorterStemmer

    def __init__(self, *args, **kwargs):
        super(Stemmer, self).__init__(*args, **kwargs)
        self.stemmer = self.stemmer_class()

    def limit(self, nodeset):
        return nodeset.filter(is_content_type=True)

    def stem(self, text):
        for sentence in nltk.sent_tokenize(text):
            for token in nltk.word_tokenize(sentence):
                stemmed_word = self.stemmer.stem(token)
                yield stemmed_word.lower()

    def apply(self, node):
        stemmed_words = node.setdefault('stemmed_words', set())
        text = node.node.astext()
        for word in self.stem(text):
            stemmed_words.add(word)
