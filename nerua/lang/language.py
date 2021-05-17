import os
import re
import six
import json
from abc import ABC


LANGUAGES = (
    ("ua", "Ukrainian"),
)

ACCENT = six.unichr(769)


class Language(ABC):
    def __init__(self):
        from nerua.lang.vocabulary import Vocabulary

        self._word_tokenization_rules = re.compile("", re.UNICODE | re.VERBOSE)
        self._punctuation_symbols = tuple()

        self._vowels = ""
        self._perfective = ""
        self._reflexive = ""
        self._adjective = ""
        self._participle = ""
        self._verb = ""
        self._noun = ""

        lang_short_name = dict(reversed(lang_tuple) for lang_tuple in LANGUAGES)[type(self).__name__]

        abbr_file_path = os.path.join(os.path.dirname(__file__), f"{lang_short_name}_abbr.json")
        if not os.path.exists(abbr_file_path):
            self._abbreviations = dict()
        else:
            self._abbreviations = json.load(abbr_file_path)

        vocab_file_path = os.path.join(os.path.dirname(__file__), "__data__", f"{lang_short_name}_vocab.json")

        if not os.path.exists(vocab_file_path):
            self._vocab = Vocabulary.create_empty(lang_short_name)
        else:
            self._vocab = Vocabulary(vocab_file_path)

    short_form = property(lambda self: dict([reversed(lang_info) for lang_info in LANGUAGES])[type(self).__name__])

    word_tokenization_rules = property(lambda self: self._word_tokenization_rules)

    punctuation_symbols = property(lambda self: self._punctuation_symbols)

    vowels = property(lambda self: self._vowels)

    perfective = property(lambda self: self._perfective)

    reflexive = property(lambda self: self._reflexive)

    adjective = property(lambda self: self._adjective)

    participle = property(lambda self: self._participle)

    verb = property(lambda self: self._verb)

    noun = property(lambda self: self._noun)

    abbreviations = property(lambda self: self._abbreviations)

    vocab = property(lambda self: self._vocab)


class Ukrainian(Language):
    def __init__(self):
        super(Ukrainian, self).__init__()

        self._word_tokenization_rules = re.compile(
            fr"[\w{ACCENT}]+://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+|"
            fr"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+|"
            fr"[0-9]+-[а-яА-ЯіїІЇ'’`{ACCENT}]+|"
            fr"[+-]?[0-9](?:[0-9,.-]*[0-9])?|"
            fr"[\w{ACCENT}](?:[\w'’`-{ACCENT}]?[\w{ACCENT}]+)*|"
            fr"[\w{ACCENT}].(?:\[\w{ACCENT}].)+[\w{ACCENT}]?|"
            fr"[\"#$%&*+,/:;<=>@^`~…\\⟨⟩{{}}\[|\]‒–—―«»“”‘’'№]|"
            fr"[.!?]+|"
            fr"-+",
            re.UNICODE | re.VERBOSE
        )

        self._punctuation_symbols = ('.', '!', '?', '"', "'", ',', ':', ';', '-', '(', ')')

        self._vowels = "аеиоуюяіїє"
        self._perfective = r"(ив|ивши|ившись|ыв|ывши|ывшись((?<=[ая])(в|вши|вшись)))$"
        self._reflexive = r"(с[яьи])$"
        self._adjective = r"(ими|ій|ий|а|е|ова|ове|ів|є|їй|єє|еє|я|ім|ем|им|ім|их|іх|ою|йми|іми|у|ю|ого|ому|ої)$"
        self._participle = r"(ий|ого|ому|им|ім|а|ій|у|ою|ій|і|их|йми|их)$"
        self._verb = r"(сь|ся|ив|ать|ять|у|ю|ав|али|учи|ячи|вши|ши|е|ме|ати|яти|є)$"
        self._noun = r"(а|ев|ов|е|ями|ами|еи|и|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю" \
                     r"|ия|ья|я|і|ові|ї|ею|єю|ою|є|еві|ем|єм|ів|їв|ю)$"
