import re
import six
from typing import List
from nerua.lang.language import Language


def tokenize_text(text: str, lang: Language):
    """
    tokenize input text to sentences

    :param text: input text to tokenize
    :param lang: the main language used in the text
    :return: list of sentences

    """
    text = six.text_type(text)

    spans = [match for match in re.finditer(r'\S+', text)]
    spans_count = len(spans)

    tokenized_text = list()

    cursor = 0
    for span_index, span in enumerate(spans):
        if span_index == spans_count - 1:
            tokenized_text.append(text[cursor:span.end()])

        elif text[span.end()-1] in ['.', '!', '?', '…', '»']:
            next_span = spans[span_index + 1]
            token = text[span.start():span.end()]
            tmp = token[re.search('[.!?…»]', token).start() - 1]
            next_tok = text[next_span.start():next_span.end()]

            if next_tok[0].isupper() and not tmp.isupper() and not (token[-1] != '.' or tmp[0] == '('):
                tokenized_text.append(text[cursor:span.end()])
                cursor = next_span.start()

    return [tokenize_sentence(sentence, lang) for sentence in tokenized_text]


def tokenize_sentence(text: str, lang: Language) -> List[str]:
    text = six.text_type(text)
    return [
        word
        for word in re.findall(lang.word_tokenization_rules, text)
    ]
