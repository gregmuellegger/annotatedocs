from . import Metric, PartOfSpeech
from ..nlp import get_passive_voice_phrases


__all__ = ('PassiveVoicePhrases',)


class PassiveVoicePhrases(Metric):
    required_metrics = Metric.required_metrics + [
        PartOfSpeech,
    ]

    def limit(self, nodeset):
        return nodeset.filter(type='paragraph',
                              part_of_speech_tags__exists=True)

    def apply(self, node):
        tags = node['part_of_speech_tags']
        node['passive_voice_phrases'] = get_passive_voice_phrases(tags)
