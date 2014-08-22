import pytest

from annotatedocs.nlp import get_pos_tags, get_passive_voice_phrases


class TestGetPassiveVoicePhrases(object):
    '''
    Some of the test sentences were taken from:
    http://writingcenter.unc.edu/handouts/passive-voice/
    '''

    def get_phrases(self, text):
        return get_passive_voice_phrases(
            get_pos_tags(text))

    def test_to_be(self):
        text = 'To be strocked can make you feel warm.'

        phrases = self.get_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'To be strocked'

    def test_being(self):
        text = 'Someone being pissed off, makes me pissed off.'

        phrases = self.get_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'being pissed'

    def test_was(self):
        text = 'The fish was caught by the seagull.'

        phrases = self.get_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'was caught'

    def test_were(self):
        text = 'The penguins were caught by the seals.'

        phrases = self.get_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'were caught'

    def test_has_been(self):
        text = 'The remote has been given to an person with bad taste.'

        phrases = self.get_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'has been given'

    def test_has_been_2(self):
        text = "The metropolis has been scorched by the dragon's fiery breath."

        phrases = self.get_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'has been scorched'

    def test_have_been(self):
        text = "The Exxon Company accepts that a few gallons might have been spilled."

        phrases = self.get_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'have been spilled'

    def test_with_text_between_to_be_and_verb(self):
        text = 'Why was the road crossed by the chicken?'

        phrases = self.get_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'was the road crossed'

    def test_active_voice(self):
        text = "Why did the chicken cross the road?"
        phrases = self.get_phrases(text)
        assert len(phrases) == 0

        text = "The chicken crossed the road."
        phrases = self.get_phrases(text)
        assert len(phrases) == 0

    @pytest.mark.xfail
    def test_to_be_past_participle_which_is_no_passive_voice(self):
        # These tests are failing at the moment because we are not able to
        # seperate intransitive from transitive verbs.
        # See here for full details on what is needed to accurately detect
        # passive voice: http://english.stackexchange.com/a/549/88209
        text = 'I am perplexed.'
        phrases = self.get_phrases(text)

        assert len(phrases) == 0

        text = 'You are worried.'
        phrases = self.get_phrases(text)

        assert len(phrases) == 0

        text = 'He was astonished.'
        phrases = self.get_phrases(text)

        assert len(phrases) == 0
