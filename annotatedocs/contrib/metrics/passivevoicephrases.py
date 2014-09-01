from ... import Metric, metrics
from ..nlp import get_passive_voice_phrases
from .partofspeech import PartOfSpeech


__all__ = ('PassiveVoicePhrases',)


@metrics.require(PartOfSpeech)
class PassiveVoicePhrases(Metric):
    def limit(self, nodeset):
        return nodeset.filter(type='paragraph',
                              part_of_speech_tags__exists=True)

    def apply(self, node, document):
        tags = node['part_of_speech_tags']
        phrases = get_passive_voice_phrases(tags)
        if phrases:
            node['passive_voice_phrases'] = phrases
