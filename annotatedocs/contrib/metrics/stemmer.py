import nltk
from nltk.stem.porter import PorterStemmer

from ... import Metric, NodeType, metrics


__all__ = ('Stemmer',)


@metrics.require(NodeType)
class Stemmer(Metric):
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

    def apply(self, node, document):
        stemmed_words = node.setdefault('stemmed_words', set())
        text = node.node.astext()
        for word in self.stem(text):
            stemmed_words.add(word)
