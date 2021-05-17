import re
import json
import pandas as pd
from typing import NoReturn
from operator import itemgetter

from nerua.lang.language import Language


BASE_NORMS = {
    "''": '"',
    "'S": "'s",
    "'s": "'s",
    '--': '-',
    '---': '-',
    'A$': '$',
    'C$': '$',
    'E£': '$',
    'Mex$': '$',
    'US$': '$',
    '`': "'",
    '``': '"',
    '£': '$',
    '¥': '$',
    '«': '"',
    '´': "'",
    '´´': '"',
    '»': '"',
    '।': '.',
    '৳': '$',
    '฿': '$',
    '–': '-',
    '—': '-',
    '——': '-',
    '‘': "'",
    '‘‘': '"',
    '’': "'",
    '’S': "'s",
    '’s': "'s",
    '’’': '"',
    '“': '"',
    '”': '"',
    '„': '"',
    '…': '...',
    '₣': '$',
    '₩': '$',
    '€': '$',
    '₹': '$',
    '₺': '$',
    '。': '.',
    '！': '!',
    '，': ',',
    '：': ':',
    '；': ';',
    '？': '?',
}


def remove_abbr(text: str, lang: Language) -> str:
    if not isinstance(text, str):
        raise TypeError(f"The 'text' variable must have a string type, not {type(text).__name__}")

    if not isinstance(lang, Language):
        raise TypeError("The 'lang' variable must be an object of the class 'nherited from the class 'Language'")

    return _multiple_replace(lang.abbreviations, text)


def base_normilize(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"The 'text' variable must have a string type, not {type(text).__name__}")

    return _multiple_replace(BASE_NORMS, text)


def convert_jsonl_tagged_file_to_csv(jsonl_file_path: str, lang: Language) -> NoReturn:
    from nerua.tokenizer import tokenize_sentence

    with open(jsonl_file_path) as file:
        jsonl = file.readlines()

    dataframe = pd.DataFrame(columns=["article_id", "word", "tag"])
    for data_in_json in jsonl:
        _, text, label, article_id = json.loads(data_in_json).values()

        cursor = 0
        for start_index, end_index, tag in sorted(label, key=itemgetter(0)):
            for token in tokenize_sentence(text[cursor:start_index], lang):
                dataframe = dataframe.append({"article_id": article_id, "word": token, "tag": "O"}, ignore_index=True)

            for token_id, token in enumerate(tokenize_sentence(text[start_index:end_index], lang)):
                dataframe = dataframe.append(
                    {"article_id": article_id, "word": token, "tag": f"{'B' if not token_id else 'I'}-{tag}"},
                    ignore_index=True
                )

            cursor = end_index

        if cursor != len(text):
            for token in tokenize_sentence(text[cursor:len(text)], lang):
                dataframe = dataframe.append({"article_id": article_id, "word": token, "tag": "O"}, ignore_index=True)

    dataframe.to_csv(jsonl_file_path.replace('.jsonl', '.csv'))


def get_text_from_jsonl_tagged_file(jsonl_file_path: str) -> str:
    with open(jsonl_file_path) as file:
        jsonl = file.readlines()

    return "".join(list(json.loads(data_in_json).values())[1] for data_in_json in jsonl)


def _multiple_replace(replacements: dict, text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"The 'text' variable must have a string type, not {type(text).__name__}")

    if not isinstance(replacements, dict):
        raise TypeError(f"The 'replacements' variable must have a dict type, not {type(text).__name__}")

    for change_from, change_to in replacements.items():
        text = re.sub(change_from, change_to, text)
    return text
