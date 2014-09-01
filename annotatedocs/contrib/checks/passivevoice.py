from ... import Check, Hint, metrics
from ..metrics.passivevoicephrases import PassiveVoicePhrases


__all__ = ('PassiveVoice',)


@metrics.require(PassiveVoicePhrases)
class PassiveVoice(Check):
    message = Hint(
        'The paragraph contains the phrase {phrase} which is put in passive '
        'voice. Consider making this active voice to be clearer about what '
        'you try to say.')

    def limit(self, nodeset):
        return nodeset.filter(passive_voice_phrases__exists=True)

    def check(self, nodeset, document):
        for node in nodeset.all():
            phrases = node['passive_voice_phrases']
            phrases = ['"{0}"'.format(phrase) for phrase in phrases]
            phrases = ', '.join(phrases)
            node.annotate(
                self.message.format(phrase=phrases))
