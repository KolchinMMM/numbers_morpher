from stanza_json import process_num, contains_num
from process_word import switch_case
import stanza
import re
import csv
from tqdm import trange


months = {
    "01": "января",
    "02": "февраля",
    "03": "марта",
    "04": "апреля",
    "05": "мая",
    "06": "июня",
    "07": "июля",
    "08": "августа",
    "09": "сентября",
    "10": "октября",
    "11": "ноября",
    "12": "декабря",
}


def replace_date(dat):
    dat = dat.replace("/", ".").replace(":", ".")
    frags = re.split("[.]", dat)
    if frags[1] not in months.keys():
        return -1
    return f"{switch_case(frags[0], 'Gen', 'masc', 'sing', 'ADJ')} {months[frags[1]]} {switch_case(frags[2], 'Gen', 'masc', 'sing', 'ADJ')} года"


def change_dvoetoch(sentence):
    to_process = re.findall("[0-9]+[:][0-9]+", sentence)
    for number in to_process:
        splitted = number.split(":")
        if len(splitted) != 2:
            break
        if int(splitted[1]) < 60 and int(splitted[0]) < 24 and len(splitted[1]) == 2:
            newer = switch_case(splitted[0], "Nom", "masc", "sing", "NUM")
            if (len(splitted[0]) == 2 and splitted[0][0] == "1") or int(splitted[0][-1]) >= 5 or splitted[0][-1] == "0":
                newer += " часов "
            elif splitted[0][-1] == "1":
                newer += " час "
            else:
                newer += " часа "
            newer += switch_case(splitted[1], "Acc", "masc", "sing", "NUM")
            minute = splitted[1]

            if (len(minute) == 2 and (minute[0] == "1" or minute[1] == "0")) or int(minute) in range(5, 10):
                newer += " минут"
            elif minute[-1] == "1" and minute != "11":
                newer += " минута"
            else:
                newer += " минуты"
        else:
            newer = f'{switch_case(splitted[0], "Nom", "masc", "sing", "NUM")}:{switch_case(splitted[1], "Nom", "masc", "sing", "NUM")}'
        sentence = sentence.replace(number, newer)

    return sentence


def change_diapazones(text):
    nlpied = nlp(text)
    for sentence in nlpied.sentences:
        new_sentence = sentence.text

        dates = re.findall('[0123][0-9][./:][01][0-9][./:][0-9]{4}', new_sentence)
        if dates:
            for date in dates:
                a = replace_date(date)
                if a != -1:
                    new_sentence = new_sentence.replace(date, a)

        new_sentence = change_dvoetoch(new_sentence)


        years_in_brackets = re.findall("[(][0-9]+[—–−-][0-9]+[)]", new_sentence)
        if years_in_brackets:
            for year in years_in_brackets:
                year = year[1:-1]
                for word in re.split("[—–−-]", year):
                    a = switch_case(word, "Nom", "masc", "sing", "ADJ")
                    new_sentence = new_sentence.replace(word, a)

        diaps = re.findall("[0-9]+[—–−-][0-9,.]+", new_sentence)

        if diaps:
            for diap in diaps:
                words = re.split("[—–−-]", diap)
                is_year = False
                for word in sentence.words:
                    if words[0] in word.text:
                        if sentence.words[word.head - 1].lemma == "год":
                            is_year = True
                        break
                if is_year:
                    new_seq = f"с {switch_case(words[0], 'Gen', 'masc', 'sing', 'ADJ')} по {switch_case(''.join(words[1:]), 'Acc', 'masc', 'sing', 'ADJ')}"
                    for word in sentence.words:
                        if words[0] in word.text and word.id != 1:
                            if sentence.words[word.id - 2].lemma == "в":
                                new_seq = f"{switch_case(words[0], 'Loc', 'masc', 'sing', 'ADJ')} по {switch_case(''.join(words[1:]), 'Acc', 'masc', 'sing', 'ADJ')}"

                else:
                    new_seq = f"от {switch_case(words[0], 'Gen', 'masc', 'sing', 'NUM')} до {switch_case(''.join(words[1:]), 'Gen', 'masc', 'sing', 'NUM')}"
                    for word in sentence.words:
                        if words[0] in word.text and word.id != 1:
                            if sentence.words[word.id - 2].lemma == "в":
                                new_seq = f"{switch_case(words[0], 'Gen', 'masc', 'sing', 'NUM')} до {switch_case(''.join(words[1:]), 'Gen', 'masc', 'sing', 'NUM')}"
                new_sentence = new_sentence.replace(diap, new_seq)

        # for word in sentence.words:
        #     if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
        #         struct = process_num(word, sentence, word.deprel, word.text)
        #         new_word = switch_case(word.text, struct["case"], struct["gender"], struct["number"], struct["type"])
        #         new_sentence = new_sentence.replace(word.text, new_word.strip())
        #print(sentence.text)
        #print(new_sentence+"\n")
        writer.writerow([sentence.text, new_sentence])


nlp = stanza.Pipeline('ru', download_method=False, warnings=False)

f = open('big_time.csv', 'w', newline='', encoding="utf-8")
writer = csv.writer(f)
writer.writerow(["q", "a"])

with open("times/big.txt", encoding="utf-8") as file:
    texts = file.read().split("\n")

#
# while True:
#     s = str(input(":"))
#     if s == "":
#         exit()
#     change_diapazones(s)

for text in trange(len(texts)):
    change_diapazones(texts[text])


