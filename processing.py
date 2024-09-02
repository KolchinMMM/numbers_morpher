from stanza_json import process_num, contains_num
from process_word import switch_case
import stanza
import json
import compare

nlp = stanza.Pipeline('ru', download_method=False, warnings=False)

with open("times/main_diapazon.txt", encoding="utf-8") as file:
    things = file.read()

d = dict(json.loads(things))

file_wrong = open("wrong.txt", "w", encoding="utf-8")
file_right = open("right.txt", "w", encoding="utf-8")
# «6 июля» М. Ф. Шатрова — Ленин
count = 0
count_correct = 0
count_wrong = 0
count_correct_one = 0
count_wrong_one = 0
count_by_words_all = 0
count_by_words_right = 0
for correct, s in d.items():
    count += 1
    print(count)
    if count > 10000:
        break
    if count >= 0:
        nlpied = nlp(s)
        for sentence in nlpied.sentences:

            new_sentence = sentence.text
            print(new_sentence)
            for word in sentence.words:
                print(word)
                if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
                    struct = process_num(word, sentence, word.deprel, word.text)
                    new_word = switch_case(word.text, struct["case"], struct["gender"], struct["number"], struct["type"])
                    new_sentence = new_sentence.replace(word.text, new_word.strip())
            print(new_sentence)
            j = compare.compare(correct, new_sentence)
            count_by_words_all += j[1]
            count_by_words_right += j[0]
            if new_sentence.lower() == correct.lower():
                count_correct += 1
                if "1" in sentence.text:
                    count_correct_one += 1
            else:
                print("WRONG! А нужно: " + correct.lower())
                if "1" in sentence.text:
                    print(sentence.text)
                    count_wrong_one += 1
                count_wrong += 1
                file_right.write(s+"\n")
                file_wrong.write(new_sentence+"\n")


file_wrong.close()
print(f"Всего правильно: {count_correct}\nВсего неправильно: {count_wrong}\nПравильно 1: {count_correct_one}\nНеправильно 1: {count_wrong_one}")
print(f"Acc: {count_correct/(count_wrong + count_correct)}\nAcc (без 1): {(count_correct - count_correct_one)/(count_correct+count_wrong - count_correct_one - count_wrong_one)}\nAcc (только 1): {count_correct_one/(count_wrong_one+ count_correct_one)}")
print(f"По словам отдельно:\nAcc: {count_by_words_right/count_by_words_all}({count_by_words_right}/{count_by_words_all})")