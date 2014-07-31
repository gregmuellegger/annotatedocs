from . import Annotation, Hint
from ..metrics import Metric, NodeType
from ..nlp import get_pos_tags, get_passive_voice_phrases


__all__ = ('PassiveVoice',)


class PartOfSpeechTagging(Metric):
    required_metrics = Metric.required_metrics + [
        NodeType,
    ]

    def limit(self, nodeset):
        return nodeset.filter(type='paragraph')

    def apply(self, node):
        raw_node = node.node
        node['part_of_speech_tags'] = get_pos_tags(raw_node.astext())


class PassiveVoicePhrases(Metric):
    required_metrics = Metric.required_metrics + [
        PartOfSpeechTagging,
    ]

    def limit(self, nodeset):
        return nodeset.filter(type='paragraph',
                              part_of_speech_tags__exists=True)

    def apply(self, node):
        tags = node['part_of_speech_tags']
        node['passive_voice_phrases'] = get_passive_voice_phrases(tags)


class PassiveVoice(Annotation):
    required_metrics = Annotation.required_metrics + [
        PassiveVoicePhrases,
    ]

    message = Hint(
        'The paragraph contains the phrase {phrase} which is put in passive '
        'voice. Consider making this active voice to be clearer about what '
        'you try to say.')

    def limit(self, nodeset):
        return nodeset.filter(passive_voice_phrases__exists=True)

    def apply(self, nodeset, document):
        for node in nodeset.all():
            phrases = node['passive_voice_phrases']
            phrases = ['"{0}"'.format(phrase) for phrase in phrases]
            phrases = ', '.join(phrases)
            node.annotate(
                self.message.format(phrase=phrases))
