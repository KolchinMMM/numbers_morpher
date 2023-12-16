import stanza
import deplacy
import re
import json

stanza_cases = dict_cases = {
    "Nom": "именительный",
    "Gen": "родительный",
    "Dat": "дательный",
    "Acc": "винительный",
    "Ins": "творительный",
    "Loc": "предложный",
}


def contains_num(s):
    return any(i.isdigit() for i in s)


def is_numeric(word):
    return word.upos in ["NUM", "ADJ"] and contains_num(word.text)


def get_params(feats):
    case = gend = num = ""
    if feats is None:
        return -1
    if "|" not in feats:
        return -1
    for feat in feats.split("|"):
        if re.match("Case=", feat):
            case = feat[5:]
        if re.match("Gender=", feat):
            gend = feat[7:]
        if re.match("Number=", feat):
            num = feat[7:]
    if num == "Plur":
        gend = "Masc"
    if case == "" or gend == "" or num == "":
        return -1

    return [case, gend, num]


def get_word_number(feats):
    if feats is None:
        return -1
    for feat in feats.split("|"):
        if re.match("Number=", feat):
            return feat[7:]
    return -1


def get_word_gender(feats):
    if feats is None:
        return -1
    for feat in feats.split("|"):
        if re.match("Gender=", feat):
            return feat[7:]
    return -1


def process_num(word, s):
    sentence_words = s.words
    # print(word)
    f = get_params(word.feats)
    print(word.text, word.feats)
    if f != -1:
        print(sentence.text)
        print(word.text)
        return {"word": word.text, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2]}

    # Найти зависимое!!!!
    if word.upos == "ADJ" and word.deprel == "nmod":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                # print(new_word)
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": word.text, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2]}


def process_sentence(s):
    sentence_words = s.words
    arr = []
    # print(len(sentence_words))
    for word in sentence_words:
        # print(word)
        if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
            arr.append(process_num(word, s))
    return arr


nlp = stanza.Pipeline('ru', download_method=None)

filename = "specific.txt"

with open(filename, "r", encoding="utf-8") as file:
    texts = file.read().split("\n")

dictionary = dict()

for line in texts:
    doc = nlp(line)
    for sentence in doc.sentences:
        dictionary[sentence.text] = process_sentence(sentence)

print(json.dumps(dictionary, ensure_ascii=False))
with open("short.json", "w", encoding="utf-8") as file:
    json.dump(dictionary, file, ensure_ascii=False, indent=4)
