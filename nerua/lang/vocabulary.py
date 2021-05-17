import os
import json
from collections import Counter

from nerua.lang.language import LANGUAGES, Language


class Vocabulary:
    def __init__(self, path: str):
        if not isinstance(path, str):
            raise TypeError

        elif not os.path.exists(path):
            raise FileNotFoundError

        lang_short_form = os.path.basename(path).partition("_")[0]
        if lang_short_form not in list(zip(*LANGUAGES))[0]:
            raise ValueError

        self._lang = dict(LANGUAGES)[lang_short_form]

        with open(path, 'r') as file:
            self._data = json.load(file)

        self._len = len(self._data)

    @staticmethod
    def from_text(text, lang: Language, *, size: int = 50000, stem_words: bool = True, **kwargs):
        from nerua.tokenizer import tokenize_sentence

        tokenized_text = tokenize_sentence(text, lang)
        if stem_words:
            from nerua.stemmer import stem_word

            tokenized_text = (stem_word(token, lang, **kwargs) for token in tokenized_text)

        vocab = Vocabulary.__new__(Vocabulary)
        vocab._lang = type(lang).__name__
        vocab._data = [word for word, _ in Counter(tokenized_text).most_common(size)]
        vocab._len = len(vocab._data)

        return vocab

    @staticmethod
    def create_empty(lang_short_name: str):
        vocab = Vocabulary.__new__(Vocabulary)
        vocab._lang = lang_short_name
        vocab._data = []
        vocab._len = 0
        return vocab

    def save(self):
        lang_short_name = dict(reversed(lang_tuple) for lang_tuple in LANGUAGES)[self._lang]
        path = os.path.join(os.path.dirname(__file__), "__data__", f"{lang_short_name}_vocab.json")

        with open(path, 'w') as file:
            json.dump(self._data, file)

    def __getitem__(self, item):
        if item in self._data:
            return self._data.index(item)

        return self._len

    def __len__(self):
        return self._len + 1
