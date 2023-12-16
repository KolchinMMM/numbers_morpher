import stanza
import re
import deplacy


def contains_num(s):
    return any(i.isdigit() for i in s)


nlp = stanza.Pipeline('ru', download_method=False)
filename = "wrong.txt"

with open(filename, "r", encoding="utf-8") as file:
    texts = file.read().split("\n")
texts = ["Экваториальная система координат имеет 2 формы: 1 и 2 экваториальные системы."]
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
