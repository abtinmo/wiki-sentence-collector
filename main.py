
from hazm import Normalizer, sent_tokenize
import os.path
import json
import urllib
import re

pagecount = 0
pages = []


def get_page():
    global pages
    if len(pages) < 1:
        response = json.loads(urllib.request.urlopen(
            "https://fa.wikipedia.org/w/api.php?format=json&action=query"
            "&generator=random&grnnamespace=0&grnlimit=1000"
            ).read())
        pages += [
            page["title"] for id, page in response["query"]["pages"].items()
            ]

    return pages.pop()


def get_page_text(title):
    title = urllib.parse.quote(title)
    response = json.loads(urllib.request.urlopen(
        f"https://fa.wikipedia.org/w/api.php?action=query&titles={title}"
        "&prop=extracts&format=json&explaintext=1&"
        "exsectionformat=plain&redirects=1"
        ).read())
    page_id = list(response["query"]["pages"].values())[0]["pageid"]
    if os.path.isfile(f'cache/{page_id}.txt'):
        # wiki articel has been parsed befor
        return False
    else:
        open(f'cache/{page_id}.txt', 'a').close()
    text = list(response["query"]["pages"].values())[0]["extract"].lower()
    return text


def has_number(text: str):
    return any([char.isnumeric() for char in text])


def has_only_farsi_char(text: str):
    return re.match("[\u0600-\u06FF| |.]+$", text)


def is_in_common_words(text: str):
    return text.startswith("جستارهای وابسته") or \
                text.startswith("پیوند به بیرون")


def has_valid_length(text: str, min_length=3, max_length=14):
    return min_length <= len(text.split()) <= max_length


def apply_common_voice_rulls(text):
    if not has_valid_length(text) or \
            has_number(text) or \
            is_in_common_words(text) or not \
            has_only_farsi_char(text):
        return None
    else:
        return text


if __name__ == '__main__':
    page_limit = 10000
    page_count = 0
    normalizer = Normalizer()
    while page_count < page_limit:
        text = get_page_text(get_page())
        if not text:
            continue
        normalaized_text = normalizer.normalize(text)
        for sentence in sent_tokenize(normalaized_text):
            if valid_sentence := apply_common_voice_rulls(sentence):
                with open('sentences.txt', 'a') as f:
                    page_count += 1
                    f.write(f"{valid_sentence}\n")
                    print(valid_sentence)
