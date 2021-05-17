import re


def preprocess_spider_data(text: str):
    if not isinstance(text, str):
        raise TypeError("The text must have a string type")

    text = re.sub(r"\xa0", " ", text)

    text = re.sub(r"<!--([\S\s]*?)-->", "", text)

    for word in ["Джерело", "Деталі", "Нагадаємо", "Передісторія"]:
        text = re.sub(fr"<[^>]*>{word}\s*:?\s*</[^>]*>\s*:?", "", text)

    # delete script tags with code inside
    text = re.sub(r"<script[^>]*>([\S\s]*?)</script>", "", text)

    text = re.sub(r"<span[^>]*>([\S\s]*?)</span>", r"\1", text)

    text = re.sub(r"<a[^>]*>([\S\s]*?)</a>", r"\1", text)

    text = re.sub(r"<strong[^>]*>([\S\s]*?)</strong>", r"\1", text)
    text = re.sub(r"<b[^>]*>([\S\s]*?)</b>", r"\1", text)

    text = re.sub(r"<em[^>]*>([\S\s]*?)</em>", r"\1", text)

    text = re.sub(r"> ", ">", text)
    text = re.sub(r" <", "<", text)

    text = re.sub(r"<p></p>", "", text)

    return text
