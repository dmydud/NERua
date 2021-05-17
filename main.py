import os
import shutil
from pathlib import Path

from nerua.scraping.spider import run_spiders
from nerua.preprocess import get_text_from_jsonl_tagged_file, create_file_for_tagging_from_xml_file
from nerua.lang.vocabulary import Vocabulary
from nerua.lang.language import Ukrainian


def create_files_for_tagging(create_spider_data: bool = False, article_tag: str = "article", paragraph_tag: str = "p"):
    if create_spider_data:
        run_spiders()

    for spider_file_path in Path("news", "spider_data").glob("*.text"):
        jsonl_file_name = os.path.basename(spider_file_path).replace("spider_data.text", "data_for_tagging.jsonl")

        create_file_for_tagging_from_xml_file(
            input_file_path=spider_file_path,
            output_file_path=os.path.join("data", jsonl_file_name),
            article_tag=article_tag,
            paragraph_tag=paragraph_tag
        )


if __name__ == "__main__":
    run_spiders()
    # create_files_for_tagging(article_tag="text")
    # preprocess_spider_data("news/spider_data/tsn_spider_data.text")
    # convert_jsonl_tagged_file_to_csv("data/tagged_data.jsonl")
    # Vocabulary.from_text(
    #     get_text_from_jsonl_tagged_file("data/tagged_data.jsonl"),
    #     lang=Ukrainian(),
    #     size=100000
    # ).save()
