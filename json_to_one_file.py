import time
import json
import stanza
import warnings
import re

warnings.catch_warnings()

warnings.simplefilter("ignore")


def contains_num(s):
    return any(i.isdigit() for i in s)


# def contains_perv(sentence):
#     for word in razdel.tokenize(sentence.lower()):
#         if word.text.startswith('перв'):
#             return True
#     return False


dictishe = dict()

for index in range(1, 14):
    print(index)
    with open(f"dir/{index}.json", "r", encoding="utf-8") as file:
        data = file.read()
    d = dict(json.loads(data))
    for correct, s in d.items():
        if len(correct) < 1024:
            dictishe[correct.replace("ё", "е")] = s.replace("ё", "е")


with open(f"main2.json", "w", encoding="utf-8") as file:
    json.dump(dictishe, file, ensure_ascii=False, indent=4)
