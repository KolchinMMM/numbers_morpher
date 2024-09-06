from stanza_json import process_num, contains_num
from process_word import switch_case
import stanza
import json
from time import sleep


def main():
    """Конвеер для замены числительных с помощью программного решения"""
    nlp = stanza.Pipeline('ru', download_method=False, warnings=False)
    count = 0
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

if __name__ == "__main__":
    main()
