from stanza_json import process_num, contains_num
from process_word import switch_case
import stanza
import json
from time import sleep

nlp = stanza.Pipeline('ru', download_method=False, warnings=False)

# with open("dir/1.json", encoding="utf-8") as file:
#     things = file.read()
#
# d = dict(json.loads(things))
#
# with open("texts/iz.txt", encoding="utf-8") as file:
#     texts = file.read()

# texts = """успешным был только 1 поход из 4\n
# в пашто используется ещё первая инновационная буква\n
# Если побеждает 3 место, они в отправляются играть со 2 местом.\n
# Победитель между 5 и 4 местами сыграет с оставшейся командой 2 тура конференции.\n
# должности 1 секретарей земельных, районных и местных комитетов
# """
#
# texts = """сироп из кленового сока был 1 из любимых продуктов как колонистов, так и индейцев"""
count = 0
count_correct = 0
sleep(1)
s = str(input("Введите предложение для замены числительных: "))
while s != "":
    count += 1
    print(count)
    # if count >= 7000:
    #     break
    nlpied = nlp(s)
    for sentence in nlpied.sentences:
        new_sentence = sentence.text
        # print(new_sentence)
        for word in sentence.words:
            if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
                struct = process_num(word, sentence, word.deprel, word.text)
                # print(struct)
                new_word = switch_case(word.text, struct["case"], struct["gender"], struct["number"], struct["type"])
                new_sentence = new_sentence.replace(word.text, new_word.strip(), 1)
        print(new_sentence)
    s = str(input(":"))
