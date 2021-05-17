import re

from nerua.lang.language import Language, Ukrainian


def stem_word(word: str, lang: Language, *, to_lower: bool = True):
    if isinstance(lang, Ukrainian):
        return stem_ukr_word(word, to_lower=to_lower)

    raise TypeError


def stem_ukr_word(word: str, *, to_lower: bool = True) -> str:
    lang = Ukrainian()

    if not isinstance(word, str):
        raise TypeError("word must have string type")

    if to_lower:
        word = word.lower()

    match = re.search(fr"[{lang.vowels}]", word)
    if match is None:
        return word

    first_word_part, buffer = word[:match.span()[1]], word[match.span()[1]:]

    # Step 1
    buffer1 = buffer
    buffer = re.sub(lang.perfective, '', buffer)
    if buffer1 == buffer:

        buffer = re.sub(lang.reflexive, '', buffer)

        buffer1 = buffer
        buffer = re.sub(lang.adjective, '', buffer)
        if buffer1 == buffer:

            buffer1 = buffer
            buffer = re.sub(lang.verb, '', buffer)
            if buffer1 == buffer:
                buffer = re.sub(lang.noun, '', buffer)
        else:
            buffer = re.sub(lang.participle, '', buffer)

    # Step 2
    buffer = re.sub(r'и$', '', buffer)

    # Step 3
    vowels = lang.vowels
    if re.search(fr"[^{vowels}][{vowels}]+[^{vowels}]+[{vowels}].*(?<=о)сть?$", buffer):
        buffer = re.sub(r'ость$', '', buffer)

    # Step 4
    buffer1 = buffer
    buffer = re.sub(r"ь$", '', buffer)
    if buffer1 != buffer:
        buffer = re.sub(r'ейше?$', '', buffer)
        buffer = re.sub(r'нн$', u'н', buffer)

    return first_word_part + buffer
