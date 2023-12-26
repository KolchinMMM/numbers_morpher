import stanza
import re
import deplacy
import json
from stanza_json import get_word_case

def contains_num(s):
    return any(i.isdigit() for i in s)


nlp = stanza.Pipeline('ru', download_method=False)


with open("dir/1.json", encoding="utf-8") as file:
    things = file.read()
d = dict(json.loads(things))

texts = d.values()


filename = "texts/not_nummod.txt"

with open(filename, "r", encoding="utf-8") as file:
    texts = file.read().split("\n")

# texts = ["Монастырские источники утверждают что это 1 из 3 сохранившихся икон евангелиста Луки."]
freq = dict()
# 2 его подворья в Константинополе, Влах-Серай и монастырь Святого Георгия Кариписа на Принцевых островах.
for se in texts:
    d = nlp(se)
    for s in d.sentences:
        # print(s.text)
        # for t in s.words:
        #     if contains_num(t.text):
        #         print("\n@@@@@@")
        #     print(t)
        #     if contains_num(t.text):
        #         print("@@@@@@\n")

        # arr = s.words
        # for t in s.words:
        #     if (t.upos == "NUM") and contains_num(t.text) and t.deprel == "nummod":
        #         if get_word_case(arr[t.head - 1].feats) == "Dat":
        #             print(s.text)

        arr = s.words
        for t in s.words:
            if (t.upos == "NUM") and contains_num(t.text) and t.deprel == "ccomp":
                print(s.text)
                #deplacy.render(d)

        # for t in s.words:
        #     if (t.upos == "NUM") and contains_num(t.text):
        #         if t.deprel not in freq:
        #             freq[t.deprel] = 1
        #         else:
        #             freq[t.deprel] += 1
print(freq)