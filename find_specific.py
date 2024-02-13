import stanza
import re
import deplacy
import json

def is_numeric(word):
    return word.upos in ["NUM", "ADJ"] and contains_num(word.text)


def get_word_case(feats):
    if feats is None:
        return -1
    for feat in feats.split("|"):
        if re.match("Case=", feat):
            return feat[5:]
    return -1


def contains_num(s):
    return any(i.isdigit() for i in s)


nlp = stanza.Pipeline('ru', use_gpu=True, download_method=False, warnings=True)
# filename = "texts/file_middle.txt"
#
# with open(filename, "r", encoding="utf-8") as file:
#     texts = file.read().split("\n")


with open("dir/1.json", encoding="utf-8") as file:
    things = file.read()

d = dict(json.loads(things))

texts = d.values()

dictishe = dict()
count = 1
for se in texts:
    d = nlp(se)
    # deplacy.render(d)
    for s in d.sentences:
        words = s.words
        for word in words:
            if word.lemma == "из":
                print(s.text)




dictishe = dict(sorted(dictishe.items(), key=lambda item: item[1]))

for k, v in dictishe.items():
    print(k, v)
