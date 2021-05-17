import os
import re
import html
import json
from lxml import etree
from typing import NoReturn

from nerua.lang.language import Language
from nerua.preprocess import _multiple_replace, base_normilize, remove_abbr


def create_file_for_tagging_from_xml_file(input_file_path: str, output_file_path: str, lang: Language) -> NoReturn:
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"Unable to find input file by path: {input_file_path}")

    elif not input_file_path.count('.') or input_file_path.split('.')[-1] != "text":
        raise ValueError("The input file must have an text extension")

    with open(input_file_path, "r") as xml_file:
        xml = xml_file.read()

    xml = normilize_text_inside_xml(xml, lang)
    jsonl = convert_ner_xml_to_jsonl(xml)

    with open(output_file_path, "w") as jsonl_file:
        jsonl_file.write(jsonl)


def convert_ner_xml_to_jsonl(xml: str) -> str:
    if not isinstance(xml, str):
        raise TypeError(f"The 'text' variable must have a string type, not {type(xml).__name__}")

    root = etree.fromstring(xml)

    jsonl = list()

    for article_id, article in enumerate(root.findall(f".//article")):

        # extract the text of the article from the paragraph tags
        article_text = "\n".join(
            paragraph.text
            for paragraph in article.findall(f".//p")
            if paragraph.text is not None
        )

        # decode html entities to utf-8
        article_text = html.unescape(article_text)

        jsonl.append(
            json.dumps({
                f"article_id": article_id,
                "article": article_text
            })
        )

    return "\n".join(jsonl)


def normilize_text_inside_xml(xml: str, lang: Language) -> str:
    if not isinstance(xml, str):
        raise TypeError(f"The 'text' variable must have a string type, not {type(xml).__name__}")

    xml = simplify_spider_xml(xml)

    root = etree.fromstring(xml)
    for article in root.findall(f".//article"):
        for paragraph in article.findall(f".//p"):
            if paragraph.text is None:
                continue

            paragraph_text = paragraph.text
            paragraph_text = base_normilize(paragraph_text)
            paragraph_text = remove_abbr(paragraph_text, lang)
            paragraph_text = re.sub(r"\s+", " ", paragraph_text)
            paragraph.text = paragraph_text.capitalize()

    xml = etree.tostring(root, encoding='unicode')
    return xml


def simplify_spider_xml(xml: str) -> str:
    """
    Remove HTML tags from text (but not p)

    :param xml: the text to be cleared of html tags
    :return: xml text without html tags

    """
    if not isinstance(xml, str):
        raise TypeError(f"The 'xml' variable must have a string type, not {type(xml).__name__}")

    # delete html comments and script tags with code inside
    xml = re.sub(r"<!--[\S\s]*?-->|<script(?:\s.*?>|>)>.*?</script>", "", xml)

    # delete tags listed in the tuple while preserving the code inside
    for tag in ("a", "strong", "b", "em", "span", "br", "i", "meta", "img"):
        xml = re.sub(fr"</?\s*{tag}(?:\s.*?>|>)", "", xml)

    # change non-breaking space to space
    xml = re.sub(u"\xa0", u" ", xml)

    # delete empty p tags
    xml = re.sub(r"<\s*p(?:\s.*?>|>)\s*</\s*p(?:\s.*?>|>)", "", xml)

    # drop p tags attributes
    xml = _multiple_replace({r"<\s*p(?:\s.*?>|>)\s*": "<p>", r"\s*</\s*p\s*>": "</p>"}, xml)

    # delete empty lines
    xml = re.sub(r"\t+\n+", "", xml)

    # delete empty articles
    xml = re.sub(fr"\t*<.*?>\s*</.*?>\n*", "", xml)

    return xml
