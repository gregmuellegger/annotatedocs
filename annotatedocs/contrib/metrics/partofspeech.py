from ... import metrics, Metric, NodeType
from ..nlp import get_pos_tags


__all__ = ('PartOfSpeech',)


@metrics.require(NodeType)
class PartOfSpeech(Metric):
    def limit(self, nodeset):
        return nodeset.filter(type='paragraph')

    def apply(self, node, document):
        raw_node = node.node
        node['part_of_speech_tags'] = get_pos_tags(raw_node.astext())
