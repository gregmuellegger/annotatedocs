from textblob import TextBlob

from ... import Metric, NodeType, metrics
from .. import nlp


__all__ = ('Stemmer',)


@metrics.require(NodeType)
class Stemmer(Metric):
    stem_word = staticmethod(nlp.stem_word)
    word_tokenizer = staticmethod(lambda text: TextBlob(text).words)

    def limit(self, nodeset):
        return nodeset.filter(is_content_type=True)

    @classmethod
    def stem(cls, text):
        for word in cls.word_tokenizer(text):
            yield cls.stem_word(word)

    def apply(self, node, document):
        stemmed_words = node.setdefault('stemmed_words', [])
        stemmed_text = self.stem(node.node.astext())
        stemmed_words.extend(stemmed_text)
