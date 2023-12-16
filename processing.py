from stanza_json import process_num, contains_num
from process_word import switch_case
import stanza
import json


nlp = stanza.Pipeline('ru', download_method=False, warnings=False)

with open("dir/1.json", encoding="utf-8") as file:
    things = file.read()

d = dict(json.loads(things))

file_wrong = open("wrong.txt", "w", encoding="utf-8")
file_right = open("right.txt", "w", encoding="utf-8")

count = 0
count_correct = 0
for correct, s in d.items():
    count += 1
    print(count)
    if count > 10:
        break
    nlpied = nlp(s)
    for sentence in nlpied.sentences:
        new_sentence = sentence.text
        print(new_sentence)
        for word in sentence.words:
            if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
                struct = process_num(word, sentence, word.deprel, word.text)
                ahui = switch_case(word.text, struct["case"], struct["gender"], struct["number"], struct["number"])
                new_sentence = new_sentence.replace(word.text, ahui)
        print(new_sentence)
        if new_sentence == correct:
            count_correct += 1
        else:
            file_right.write(s+"\n")
            file_wrong.write(new_sentence+"\n")


file_wrong.close()
print(f"Acc: {count_correct/count} {count_correct}/{count}")




