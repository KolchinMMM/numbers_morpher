import stanza
import re
import deplacy


def contains_num(s):
    return any(i.isdigit() for i in s)


nlp = stanza.Pipeline('ru', download_method=False)
filename = "specific.txt"

with open(filename, "r", encoding="utf-8") as file:
    texts = file.read().split("\n")

for se in texts:
    d = nlp(se)
    deplacy.render(d)
    for s in d.sentences:
        for t in s.words:
            if contains_num(t.text):
                print("\n@@@@@@")
            print(t)
            if contains_num(t.text):
                print("@@@@@@\n")
