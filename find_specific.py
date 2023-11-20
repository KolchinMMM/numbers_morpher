import stanza
import re
import deplacy


def contains_num(s):
    return any(i.isdigit() for i in s)


nlp = stanza.Pipeline('ru', use_gpu=True, download_method=False, warnings=True)
filename = "texts/file_middle.txt"

with open(filename, "r", encoding="utf-8") as file:
    texts = file.read().split("\n")

count = 1
for se in texts:
    d = nlp(se)
    # deplacy.render(d)
    for s in d.sentences:
        for t in s.words:
            if t.upos == "NUM" and (t.deprel == "nummod"):
                if contains_num(t.text):
                    # print(t.deprel+":")
                    print(s.text)


