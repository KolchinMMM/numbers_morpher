import stanza
import re
import deplacy
import json
from stanza_json import get_word_case


def contains_num(s):
    return any(i.isdigit() for i in s)


def is_numeric(word):
    return word.upos in ["NUM", "ADJ"] and contains_num(word.text)


nlp = stanza.Pipeline('ru', download_method=False)


# with open("dir/1.json", encoding="utf-8") as file:
#     things = file.read()
# d = dict(json.loads(things))
#
# texts = d.values()


filename = "datasets/texts/specific.txt"

with open(filename, "r", encoding="utf-8") as file:
    texts = file.read().split("\n")

texts = """12 и 13 сентября""".split("\n")
freq = dict()
for se in texts:
    d = nlp(se)

    for s in d.sentences:
        print(s.text)
        deplacy.render(d)
        for t in s.words:
            # if contains_num(t.text):
            #     print("\n@@@@@@")
            print(t)
            # if contains_num(t.text):
            #     print("@@@@@@\n")

        # arr = s.words
        # for t in s.words:
        #     if (t.upos == "NUM") and contains_num(t.text) and t.deprel == "nummod":
        #         if get_word_case(arr[t.head - 1].feats) == "Gen":
        #             print(s.text)

        # arr = s.words
        # for t in s.words:
        #     if (t.upos == "NUM") and contains_num(t.text) and t.deprel == "conj":
        #         print(s.text)
        #         #deplacy.render(d)
        # for t in s.words:
        #     if t.lemma == "из":
        #         print(s.text)
        # for t in s.words:
        #     if (t.upos == "NUM") and contains_num(t.text):
        #         if t.deprel not in freq:
        #             freq[t.deprel] = 1
        #         else:
        #             freq[t.deprel] += 1
