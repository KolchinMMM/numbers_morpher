import stanza
import deplacy
import re
import json
from time import perf_counter


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


def get_word_case(feats):
    if feats is None:
        return -1
    for feat in feats.split("|"):
        if re.match("Case=", feat):
            return feat[5:]
    return -1


def process_num(word, s, deprel, original_number):
    sentence_words = s.words
    num = get_word_number(word.feats)
    case = get_word_case(word.feats)
    gender = get_word_gender(word.feats)
    if case != -1:
        if num == "Plur":
            return {"word": original_number, "type": word.upos, "case": case, "gender": "Masc", "number": num, "deprel": deprel}
        else:
            if gender != -1:
                return {"word": original_number, "type": word.upos, "case": case, "gender": gender, "number": "Sing", "deprel": deprel}

    # порядковое числительное как дополнение к существительному
    if word.upos == "ADJ" and word.deprel == "nmod":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}

    # Всегда как дата
    if word.upos == "ADJ" and word.deprel == "obl":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                gender = get_word_gender(new_word.feats)
                number = get_word_number(new_word.feats)
                if gender != -1 and number != -1:
                    return {"word": original_number, "type": word.upos, "case": "Gen", "gender": gender, "number": number, "deprel": deprel}

    # Числительное внутри скобок, похоже на nmod
    if word.upos == "ADJ" and word.deprel == "parataxis":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}
        f = get_params(sentence_words[word.head - 1].feats)
        if f != -1:
            return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}

    if word.upos == "ADJ" and word.deprel == "amod":
        f = get_params(sentence_words[word.head - 1].feats)
        if f != -1:
            return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}

    # Числительное в роли подлежащего
    if word.upos == "ADJ" and word.deprel == "nsubj":
        gender = get_word_gender(sentence_words[word.head - 1].feats)
        number = get_word_number(sentence_words[word.head - 1].feats)
        if number == -1:
            if gender != -1:
                return {"word": original_number, "type": word.upos, "case": "Nom", "gender": gender, "number": "Sing", "deprel": deprel}
        if gender != -1:
            return {"word": original_number, "type": word.upos, "case": "Nom", "gender": gender, "number": number, "deprel": deprel}

    if word.upos == "ADJ" and word.deprel == "fixed":
        f = get_params(sentence_words[word.head - 1].feats)
        if f != -1:
            return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}

    if word.upos == "ADJ" and word.deprel == "root":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos == "NOUN":
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}

    # Однородное числительное
    if word.deprel == "conj":
        if is_numeric(sentence_words[word.head - 1]):
            return process_num(sentence_words[word.head - 1], s, deprel, original_number)
        for wrd in sentence_words:
            if wrd.head == word.id:
                f = get_params(wrd.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "root":
        for new_word in sentence_words:
            if new_word.head == word.head:
                if new_word.deprel == "flat":
                    case = get_word_case(new_word.feats)
                    num = get_word_number(new_word.feats)
                    gen = get_word_gender(new_word.feats)
                    if num == "Plur":
                        return {"word": original_number, "type": "ADJ", "case": case, "gender": "Masc",
                                "number": "Plur", "deprel": deprel}
                    else:
                        return {"word": original_number, "type": "ADJ", "case": case, "gender": gen,
                                "number": "Sing", "deprel": deprel}
        for new_word in sentence_words:
            if new_word.head == word.head:
                if new_word.upos == "ADP":
                    case = get_word_case(new_word.feats)
                    num = get_word_number(new_word.feats)
                    gen = get_word_gender(new_word.feats)
                    if num == "Plur":
                        return {"word": original_number, "type": "NUM", "case": case, "gender": "Masc",
                                "number": "Plur", "deprel": deprel}
                    else:
                        return {"word": original_number, "type": "NUM", "case": case, "gender": gen,
                                "number": "Sing", "deprel": deprel}
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc",
                "number": "Sing", "deprel": deprel}

    #  Числительное является подлежащим, необходимо найти число по глаголу.
    if word.deprel == "nsubj" and word.upos == "NUM":
        if word.head != 0:
            wrd = sentence_words[word.head - 1]
            gender = get_word_gender(wrd.feats)
            number = get_word_number(wrd.feats)
            return {"word": original_number, "type": word.upos, "case": "Nom", "gender": gender, "number": number, "deprel": deprel}
        return {"word": original_number, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing", "deprel": deprel}

    # Числительное с опущенным зависимым существительным. Если стоит с наречием - РП, иначе - ИП
    if word.deprel == "nsubj:pass":
        case = "Nom"
        for elem in sentence_words:
            if elem.head == word.id and elem.upos == "ADP":
                case = "Gen"
        return {"word": original_number, "type": word.upos, "case": case, "gender": "Masc", "number": "Sing", "deprel": deprel}

    if re.match("nummod", word.deprel):
        flag = True
        for elem in sentence_words:
            if elem.head == word.id and elem.upos == "ADP":
                flag = False
        if flag:
            return {"word": original_number, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing", "deprel": deprel}
        head_word = sentence_words[word.head - 1]
        f = get_params(head_word.feats)
        if f != -1:
            return {"word": original_number, "type": "NUM", "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}

    # Числительное как приложение
    if word.deprel == "appos":
        return {"word": original_number, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing", "deprel": deprel}

    # Числительное - дополнение
    if word.upos == "NUM" and word.deprel == "nmod":
        # Если оно зависит от другого числительного
        if is_numeric(sentence_words[word.head - 1]):
            return process_num(sentence_words[word.head - 1], s, deprel, original_number)
        for wrd in sentence_words:
            if wrd.head == word.id:
                f = get_params(wrd.feats)
                if f != -1:
                    return {"word": original_number, "type": "ADJ", "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "parataxis":
        for wrd in sentence_words:
            if wrd.head == word.id:
                if wrd.deprel == "flat":
                    f = get_params(wrd.feats)
                    if f != -1:
                        return {"word": original_number, "type": "ADJ", "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc", "number": "Sing", "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "obl":
        for new_word in sentence_words:
            if new_word.head == word.id:
                if new_word.upos == "flat":
                    f = get_params(new_word.feats)
                    if f != -1:
                        return {"word": original_number, "type": "ADJ", "case": f[0], "gender": f[1], "number": f[2], "deprel": deprel}
        return {"word": original_number, "type": "NUM", "case": "Gen", "gender": "Masc", "number": "Sing", "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "compound":
        if is_numeric(sentence_words[word.head - 1]):
            return process_num(sentence_words[word.head - 1], s, deprel, original_number)

    if word.upos == "NUM" and word.deprel == "flat":
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc", "number": "Sing", "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "acl":
        num = get_word_number(sentence_words[word.head - 1].feats)
        if num == "Plur":
            return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc", "number": "Plur", "deprel": deprel}
        gen = get_word_gender(sentence_words[word.head - 1].feats)
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gen, "number": "Sing", "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "advcl":
        for new_word in sentence_words:
            if new_word.head == word.id:
                num = get_word_number(new_word.feats)
                if num == "Plur":
                    return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc", "number": "Plur", "deprel": deprel}
                gen = get_word_gender(new_word.feats)
                return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gen, "number": "Sing", "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "ccomp":
        gen = ""
        num = ""
        case = ""
        for new_word in sentence_words:
            if new_word.head == word.id:
                if get_word_number(new_word.feats) == "Plur":
                    num = get_word_number(new_word.feats)
                    gen = "Masc"
                if get_word_gender(new_word.feats) != -1:
                    gen = get_word_gender(new_word.feats)
                    num = "Sing"
                if new_word.upos in ["VERB", "AUX"]:
                    return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gen, "number": num, "deprel": deprel}
                else:
                    case = get_word_case(new_word.feats)
            return {"word": original_number, "type": "NUM", "case": case, "gender": gen, "number": num, "deprel": deprel}
    return {"word": original_number, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing", "deprel": deprel, "flag": "1"}


def process_sentence(s):
    sentence_words = s.words
    arr = []
    for word in sentence_words:
        if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
            arr.append(process_num(word, s, word.deprel, word.text))
    return arr


def main():
    nlp = stanza.Pipeline('ru', download_method=False, warnings=False)
    filename = "texts/better texts dump.txt"
    filename = "specific.txt"

    with open(filename, "r", encoding="utf-8") as file:
        texts = file.read().split("\n")

    dictionary = dict()
    start = perf_counter()
    for line in texts:
        doc = nlp(line)
        for sentence in doc.sentences:
            dictionary[sentence.text] = process_sentence(sentence)

    print(f"Time spent: {perf_counter() - start}")
    print(json.dumps(dictionary, ensure_ascii=False))
    with open("t.json", "w", encoding="utf-8") as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()



