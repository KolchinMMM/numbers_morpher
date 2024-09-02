import stanza
import re
from process_word import switch_case
from stanza_json import *
import csv
import pandas as pd

nlp = stanza.Pipeline('ru', download_method=False, warnings=False)


def contains_num(s):
    return any(i.isdigit() for i in s)

# re_float = '.*[+-]?[0-9]+[.,][0-9]+.*'
# sent = "Тройкой при коллегии ГПУ УССР 23.09 г. по ст. 54-2, 4, 7, 11 УК УССР, приговорён к 10 годам лагерей."
# nl = nlp(sent)
# for sentence in nl.sentences:
#     for word in sentence.words:
#         print(word.text)

text = []
with open('final_main.csv', 'r', newline='', encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if row != []:
            text.append(row[0])

file = open("MAIN.csv", "w", encoding="utf-8", newline='')
writer = csv.writer(file)
writer.writerow(["q", "a"])
for txt in text:
    flag = True
    nlpied = nlp(txt)
    for sentence in nlpied.sentences:
        new_sentence = sentence.text
        for word in sentence.words:
            if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
                if re.match('^[+-]?[0-9]+[.,][0-9]+$', word.text):
                    print(sentence.text)
                    new_word = switch_case(word.text, "Nom", "Masc", "Sing", "NUM")
                    new_sentence = new_sentence.replace(word.text, new_word)
                else:
                    flag = False
                    break
        if flag:
            # print(new_sentence)
            writer.writerow([sentence.text, new_sentence])
