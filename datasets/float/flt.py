import csv
import stanza
import re
from tqdm.auto import trange

def contains_num(s):
    return any(i.isdigit() for i in s)


f = open("main15.txt", "w", encoding="utf-8", )


nlp = stanza.Pipeline('ru', download_method=False, warnings=False)

with open("15res.txt", "r", encoding="utf-8") as file:
    reader = file.read().split("\n")
    for i in trange(len(reader)):
        nlpied = nlp(reader[i])
        flag = True
        for sentence in nlpied.sentences:
            new_sentence = sentence.text
            for word in sentence.words:
                if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
                    if not re.match('^[+-]?[0-9]+[.,][0-9]+$', word.text):
                        flag = False
                        break
            if flag:
                # print(new_sentence)
                f.write(sentence.text+"\n")
