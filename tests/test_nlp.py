from annotatedocs.nlp import get_passive_voice_phrases


class TestGetPassiveVoicePhrases(object):
    '''
    Some of the test sentences were taken from:
    http://writingcenter.unc.edu/handouts/passive-voice/
    '''

    def test_to_be(self):
        text = 'To be strocked can make you feel warm.'

        phrases = get_passive_voice_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'To be strocked'

    def test_being(self):
        text = 'Someone being pissed off, makes me pissed off.'

        phrases = get_passive_voice_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'being pissed'

    def test_was(self):
        text = 'The fish was caught by the seagull.'

        phrases = get_passive_voice_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'was caught'

    def test_were(self):
        text = 'The penguins were caught by the seals.'

        phrases = get_passive_voice_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'were caught'

    def test_has_been(self):
        text = 'The remote has been given to an person with bad taste.'

        phrases = get_passive_voice_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'has been given'

    def test_has_been_2(self):
        text = "The metropolis has been scorched by the dragon's fiery breath."

        phrases = get_passive_voice_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'has been scorched'

    def test_have_been(self):
        text = "The Exxon Company accepts that a few gallons might have been spilled."

        phrases = get_passive_voice_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'have been spilled'

    def test_with_text_between_to_be_and_verb(self):
        text = 'Why was the road crossed by the chicken?'

        phrases = get_passive_voice_phrases(text)
        assert len(phrases) == 1
        assert phrases[0] == 'was the road crossed'

    def test_active_voice(self):
        text = "Why did the chicken cross the road?"
        assert get_passive_voice_phrases(text) == []

        text = "The chicken crossed the road."
        assert get_passive_voice_phrases(text) == []
