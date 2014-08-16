from __future__ import division

import nltk

from .base import Metric
from .nodetype import NodeType


__all__ = ('WordStats',)


class WordStats(Metric):
    '''
    Adds some statistics like average word length, sentence length etc.
    '''

    required_metrics = Metric.required_metrics + [
        NodeType,
    ]

    def limit(self, nodeset):
        return nodeset.filter(is_content_type=True)

    def apply(self, node, document):
        text = node.node.astext()
        sentences = [
            nltk.word_tokenize(sentence)
            for sentence in nltk.sent_tokenize(text)]

        word_count = sum([len(sentence) for sentence in sentences])
        sentence_count = len(sentences)

        node['word_count'] = word_count
        node['sentence_count'] = sentence_count
        node['avg_sentence_length'] = word_count / sentence_count
