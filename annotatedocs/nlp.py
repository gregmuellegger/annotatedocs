from textblob import TextBlob
from textblob_aptagger import PerceptronTagger


FORMS_OF_TO_BE = (
    'to be',
    'be',
    'being',
    'was',
    'were',
    'has been',
    'have been',
    'will be',
    'will have been',
)


VERB_PAST_PARTICIBLE = 'VBN'


# Maybe speedup the startup.
pos_tagger = PerceptronTagger()


def is_to_be(tags, position):
    '''
    Returns a positive number if the tags contain a form of to be at
    ``position``. The returned number indicates the length of the to be part,
    so "to be" would return 2, "was" returns 1, and "will have been" 3, etc.

    If ``tags`` to not have a form of 'to be' in ``position``, return 0.
    '''
    for to_be in FORMS_OF_TO_BE:
        to_be_parts = to_be.split()
        words = []
        for i in range(len(to_be_parts)):
            try:
                word, part_of_speech = tags[position + i]
            except IndexError:
                # In case we run out of words, we did not find a match.
                return 0
            # Normalize word, by making it lowercase.
            words.append(word.lower())
        if words == to_be_parts:
            return len(words)
    return 0


def index_passive_voice_phrase(tags, position):
    to_be_word_length = is_to_be(tags, position)
    if to_be_word_length:
        start = position + to_be_word_length
        for next_pos, next_tag in enumerate(tags[start:]):
            if next_tag[1] == VERB_PAST_PARTICIBLE:
                return next_pos + to_be_word_length
    return -1


def get_passive_voice_phrases(text):
    '''
    Returns a list of phrases that seem to be in passive voice.
    '''
    blob = TextBlob(text, pos_tagger=pos_tagger)
    tags = blob.tags
    passive_voice_phrases = []
    i = 0
    while i < len(tags):
        offset = index_passive_voice_phrase(tags, i)
        if offset != -1:
            passive_voice_phrases.append(tags[i:i + offset + 1])
            # Jump to the end of the phrase.
            i = i + offset
        i += 1
    return [
        ' '.join(word for word, pos in phrase)
        for phrase in passive_voice_phrases]
