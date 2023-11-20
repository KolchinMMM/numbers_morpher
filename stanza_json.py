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
    if "|" not in feats:
        return -1
    for feat in feats.split("|"):
        if re.match("Case=", feat):
            case = feat[5:]
        if re.match("Gender=", feat):
            gend = feat[7:]
        if re.match("Number=", feat):
            num = feat[7:]
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
    if re.match('.*[a-zA-Zа-яА-Я].*', word.text):
        f = get_params(word.feats)
        if f != -1:
            return {"word": word.text, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2]}
        else:
            raise Exception("Инородные буквы")

    # порядковое числительное как дополнение к существительному
    if word.upos == "ADJ" and word.deprel == "nmod":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": word.text, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2]}

    # Всегда как дата
    if word.upos == "ADJ" and word.deprel == "obl":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                gender = get_word_gender(new_word.feats)
                number = get_word_number(new_word.feats)
                if gender != -1 and number != -1:
                    return {"word": word.text, "type": word.upos, "case": "Gen", "gender": gender, "number": number}

    # Числительное внутри скобок, похоже на nmod
    if word.upos == "ADJ" and word.deprel == "parataxis":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": word.text, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2]}

    if word.upos == "ADJ" and word.deprel == "amod":
        pass
        # TODO

    if word.upos == "ADJ" and word.deprel == "nsubj":
        pass
        # TODO

    if word.upos == "ADJ" and word.deprel == "fixed":
        pass
        # TODO

    if word.upos == "ADJ" and word.deprel == "root":
        pass
        # TODO

    if word.upos == "ADJ" and word.deprel == "orphan":
        pass
        # TODO

    if word.upos == "ADJ" and word.deprel == "iobj":
        pass
        # TODO

    # Однородное числительное
    if word.deprel == "conj":
        if is_numeric(sentence_words[word.head - 1]):
            return process_num(sentence_words[word.head - 1], s)
        for wrd in sentence_words:
            if wrd.head == word.id:
                f = get_params(wrd.feats)
                if f != -1:
                    return {"word": word.text, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2]}

    #  Числительное является подлежащим, необходимо найти число по глаголу.
    if word.deprel == "nsubj" and word.upos == "NUM":
        if word.head != 0:
            wrd = sentence_words[word.head - 1]
            gender = get_word_gender(wrd.feats)
            number = get_word_number(wrd.feats)
            return {"word": word.text, "type": word.upos, "case": "Nom", "gender": gender, "number": number}
        return {"word": word.text, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing"}

    # ????? Числительное с опущенным зависимым существительным. Если стоит с наречием - РП, иначе - ИП
    if word.deprel == "nsubj:pass":
        case = "Nom"
        for elem in sentence_words:
            if elem.head == word.id and elem.upos == "ADP":
                case = "Gen"
        return {"word": word.text, "type": word.upos, "case": case, "gender": "Masc", "number": "Sing"}

    # ?????? Найти зависимое
    if word.deprel == "nummod":
        flag = True
        for elem in sentence_words:
            if elem.head == word.id and elem.upos == "ADP":
                flag = False
        if flag:
            return {"word": word.text, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing"}
        head_word = sentence_words[word.head - 1]
        f = get_params(head_word.feats)
        if f != -1:
            return {"word": word.text, "type": "NUM", "case": f[0], "gender": f[1], "number": f[2]}

    # Числительное как приложение
    if word.deprel == "appos":
        return {"word": word.text, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing"}

    # Числительное - дополнение
    if word.upos == "NUM" and word.deprel == "nmod":
        # Если оно зависит от другого числительного
        if is_numeric(sentence_words[word.head - 1]):
            return process_num(sentence_words[word.head - 1], s)
        for wrd in sentence_words:
            if wrd.head == word.id:
                f = get_params(wrd.feats)
                if f != -1:
                    return {"word": word.text, "type": "ADJ", "case": f[0], "gender": f[1], "number": f[2]}

    if word.upos == "NUM" and word.deprel == "parataxis":
        pass
        # TODO

    if word.upos == "NUM" and word.deprel == "obj":
        pass
        # TODO

    if word.upos == "NUM" and word.deprel == "obl":
        for new_word in sentence_words:
            if new_word.head == word.id:
                if new_word.upos == "flat":
                    f = get_params(new_word.feats)
                    if f != -1:
                        return {"word": word.text, "type": "ADJ", "case": f[0], "gender": f[1], "number": f[2]}
        return {"word": word.text, "type": "NUM", "case": "Gen", "gender": "Masc", "number": "Sing"}

    if word.upos == "NUM" and word.deprel == "compound":
        pass
        # TODO

    if word.upos == "NUM" and word.deprel == "flat":
        pass
        # TODO

    if word.upos == "NUM" and word.deprel == "det":
        pass
        # TODO

    if word.upos == "NUM" and word.deprel == "acl":
        pass
        # TODO

    if word.upos == "NUM" and word.deprel == "advcl":
        pass
        # TODO

    if word.upos == "NUM" and word.deprel == "fixed":
        pass
        # TODO

    if word.upos == "NUM" and word.deprel == "ccomp":
        pass
        # TODO


def process_sentence(s):
    sentence_words = s.words
    arr = []
    # print(len(sentence_words))
    for word in sentence_words:
        # print(word)
        if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
            arr.append(process_num(word, s))
    return arr


def contains_num(s):
    return any(i.isdigit() for i in s)


nlp = stanza.Pipeline('ru')

filename = "specific.txt"

with open(filename, "r", encoding="utf-8") as file:
    texts = file.read().split("\n")

dictionary = dict()

for line in texts:
    doc = nlp(line)
    for sentence in doc.sentences:
        dictionary[sentence.text] = process_sentence(sentence)

print(json.dumps(dictionary, ensure_ascii=False))
with open("text.json", "w", encoding="utf-8") as file:
    json.dump(dictionary, file, ensure_ascii=False, indent=4)
