import stanza
import deplacy
import re
import json
from time import perf_counter

dict_adps_for_cases = {
    "Gen": ["от", "до", "около", "вокруг", "после", "кроме", "из", "без", "для"],
    "Dat": ["к", "по"],
    "Acc": ["в", "за", "про", "через"],
    "Ins": ["с", "за", "под", "над", "между"],
    "Loc": ["о", "об", "при"],
}

stanza_cases = dict_cases = {
    "Nom": "именительный",
    "Gen": "родительный",
    "Dat": "дательный",
    "Acc": "винительный",
    "Ins": "творительный",
    "Loc": "предложный",
}


def get_case_by_adp(adp):
    for i, v in dict_adps_for_cases.items():
        if adp in v:
            return i
    return -1


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


def has_word(words, index1, index2, arr_search):
    start = min(index1, index2)
    end = max(index1, index2)
    for i in range(start, end):
        if words[i].lemma in arr_search:
            return True
    return False


def process_num(word, s, deprel, original_number):
    sentence_words = s.words
    num = get_word_number(word.feats)
    case = get_word_case(word.feats)
    gender = get_word_gender(word.feats)
    # for n_word in sentence_words:
    #     if (n_word.id < word.id or n_word.lemma == "из") and n_word.head == word.id and n_word.upos == "ADP":
    #         f1 = get_case_by_adp(n_word.lemma)
    #         if f1 != -1:
    #             type = "NUM"
    #             case = f1
    #             if n_word.lemma == "из":
    #                 break
    #             if word.deprel in ["obl"]:
    #                 for new_word in sentence_words:
    #                     if new_word.head == word.id and new_word.upos in ["NOUN", "PROPN", "PRON"]:
    #                         gender = get_word_gender(new_word.feats)
    #                         num = get_word_number(new_word.feats)
    #             else:
    #                 new_word = sentence_words[word.head - 1]
    #                 gender = get_word_gender(new_word.feats)
    #                 num = get_word_number(new_word.feats)
    #
    #             for new_word in sentence_words:
    #                 if new_word.lemma == "из" and new_word.id > word.id:
    #                     num = "Sing"

    for new_word in sentence_words:
        if word.head == new_word.id or (word.id == new_word.head and word.deprel == 'obl'):
            if has_word(sentence_words, new_word.id, word.id, "из"):
                numb = "Sing"
                for iz_word in sentence_words:
                    if iz_word.lemma == "из" and iz_word.head == word.id:
                        if iz_word.id > word.id:
                            if re.match("nsubj", word.deprel):
                                if new_word.deprel == "root":
                                    case = "Gen"
                                else: # nmod
                                    case = "Nom"
                                gender = get_word_gender(new_word.feats)
                                number = get_word_number(new_word.feats)
                                return {"word": original_number, "type": word.upos, "case": case, "gender": gender,
                                        "number": number, "deprel": deprel}
                            if word.deprel == "root":
                                case = "Nom"
                                gender = "Masc"
                                number = "Sing"
                                for n_word in sentence_words:
                                    if n_word.head == word.id or n_word.id == word.head:
                                        if n_word.upos in ["VERB", "AUX"]:
                                            case = "Gen"
                                            number = "Sing"
                                        elif n_word.upos in ["NOUN", "PROPN", "PRON"]:
                                            case = get_word_case(n_word.feats)
                                return {"word": original_number, "type": word.upos, "case": case, "gender": gender,
                                        "number": number, "deprel": deprel}
                            if word.deprel == "obl":
                                case = "Nom"
                                gender = "Masc"
                                number = "Sing"
                                for n_word in sentence_words:
                                    if n_word.head == word.id or n_word.id == word.head:
                                        if n_word.upos in ["VERB", "AUX"]:
                                            case = "Gen"
                                            number = "Sing"
    cas = -1
    for new_word in sentence_words:
        if new_word.id == word.head and new_word.upos in ["NOUN", "PROPN", "PRON"]:
            for adp in sentence_words:
                if (adp.head == new_word.id or adp.head == word.id) and adp.upos == "ADP":
                    cas = get_case_by_adp(adp.text)
    if cas != -1:
        gender = get_word_gender(sentence_words[word.head - 1].feats)
        number = get_word_number(sentence_words[word.head - 1].feats)
        return {"word": original_number, "type": word.upos, "case": cas, "gender": gender, "number": number, "deprel": deprel}

    # if case != -1:
    #     if num == "Plur":
    #         return {"word": original_number, "type": word.upos, "case": case, "gender": "Masc", "number": num, "deprel": deprel}
    #     else:
    #         if gender != -1:
    #             return {"word": original_number, "type": word.upos, "case": case, "gender": gender, "number": "Sing", "deprel": deprel}



    # порядковое числительное как дополнение к существительному
    if word.upos == "ADJ" and word.deprel == "nmod":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos in ["NOUN", "PROPN", "PRON"]:
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2],
                            "deprel": deprel}

    # Всегда как дата
    if word.upos == "ADJ" and word.deprel == "obl":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos in ["NOUN", "PROPN", "PRON"]:
                gender = get_word_gender(new_word.feats)
                number = get_word_number(new_word.feats)
                if gender != -1 and number != -1:
                    return {"word": original_number, "type": word.upos, "case": "Gen", "gender": gender,
                            "number": number, "deprel": deprel}

    # Числительное внутри скобок, похоже на nmod
    if word.upos == "ADJ" and word.deprel == "parataxis":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos in ["NOUN", "PROPN", "PRON"]:
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2],
                            "deprel": deprel}
        f = get_params(sentence_words[word.head - 1].feats)
        if f != -1:
            return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2],
                    "deprel": deprel}

    if word.upos == "ADJ" and word.deprel == "amod":
        f = get_params(sentence_words[word.head - 1].feats)
        if f != -1:
            return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2],
                    "deprel": deprel}

    # Числительное в роли подлежащего
    if word.upos == "ADJ" and word.deprel == "nsubj":
        for new_word in sentence_words:
            if new_word.head == word.id:
                if new_word.upos in ["PROPN", "PRON", "NOUN"]:
                    gender = get_word_gender(new_word.feats)
                    if gender == -1:
                        gender = "Masc"
                    return {"word": original_number, "type": word.upos, "case": "Nom", "gender": gender,
                            "number": "Sing", "deprel": deprel}
        return {"word": original_number, "type": word.upos, "case": "Nom", "gender": gender, "number": "Sing",
                "deprel": deprel}

    if word.upos == "ADJ" and word.deprel == "fixed":
        f = get_params(sentence_words[word.head - 1].feats)
        if f != -1:
            return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2],
                    "deprel": deprel}
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos in ["NOUN", "PROPN", "PRON"]:
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2],
                            "deprel": deprel}

    if word.upos == "ADJ" and word.deprel == "root":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos in ["NOUN", "PROPN", "PRON"]:
                f = get_params(new_word.feats)
                if f != -1:
                    return {"word": original_number, "type": word.upos, "case": f[0], "gender": f[1], "number": f[2],
                            "deprel": deprel}

    # Однородное числительное
    if word.deprel == "conj":
        if is_numeric(sentence_words[word.head - 1]):
            return process_num(sentence_words[word.head - 1], s, deprel, original_number)

        for new_word in sentence_words:

            if new_word.head == word.id and new_word.upos in ["NOUN", "PROPN", "PRON"]:
                numb = get_word_number(new_word.feats)
                case = get_word_case(new_word.feats)
                gend = get_word_gender(new_word.feats)

                if has_word(sentence_words, word.id, new_word.id, "из"):
                    numb = "Sing"

                if case == ["Dat", "Loc", "Ins"]:
                    if original_number != "1":
                        if case == "Plur":
                            return {"word": original_number, "type": "NUM", "case": case, "gender": gend,
                                    "number": numb, "deprel": deprel}
                        else:
                            return {"word": original_number, "type": "ADJ", "case": case, "gender": gend,
                                    "number": numb, "deprel": deprel}
                    else:
                        return {"word": original_number, "type": "NUM", "case": case, "gender": gend,
                                "number": numb, "deprel": deprel}

                if case == "Gen":
                    if new_word.deprel == "nmod":
                        if numb == "Plur" or original_number == '1':
                            return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend,
                                    "number": "Plur",
                                    "deprel": deprel}
                        else:
                            return {"word": original_number, "type": "ADJ", "case": "Gen", "gender": gend,
                                    "number": "Sing",
                                    "deprel": deprel}

                    if new_word.deprel == "obl":
                        if original_number == "1":
                            # if numb == "Plur":
                            #     return {"word": original_number, "type": "ADJ", "case": "Gen", "gender": gend,
                            #             "number": numb,
                            #             "deprel": deprel}
                            # else:
                            return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend,
                                    "number": "Sing",
                                    "deprel": deprel}
                        else:
                            if numb == "Plur":
                                return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend,
                                        "number": "Sing",
                                        "deprel": deprel}
                            else:
                                return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend,
                                        "number": "Sing",
                                        "deprel": deprel}

                    return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend, "number": numb,
                            "deprel": deprel}

                if case in ["Acc", "Nom"] and original_number != "1":
                    return {"word": original_number, "type": "ADJ", "case": case, "gender": gend, "number": numb,
                            "deprel": deprel}

                if new_word.deprel == "nsubj":
                    if original_number == "1":
                        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend, "number": numb,
                                "deprel": deprel}
                    else:
                        return {"word": original_number, "type": "ADJ", "case": "Nom", "gender": gend, "number": numb,
                                "deprel": deprel}

                if new_word.deprel in ["nsubj", "obl"] or new_word.upos not in ["NOUN", "PRON", "PROPN"]:
                    case = "Nom"
                if case != -1:
                    if numb == "Plur":
                        return {"word": original_number, "type": word.upos, "case": case, "gender": "Masc",
                                "number": "Plur",
                                "deprel": deprel}
                    elif gend != -1:
                        return {"word": original_number, "type": word.upos, "case": case, "gender": gend,
                                "number": "Sing",
                                "deprel": deprel}

    # if word.upos == "NUM" and re.match("nsubj", word.deprel):
    #     if word.head != 0:
    #         new_word = sentence_words[word.head - 1]
    #         gender = get_word_gender(new_word.feats)
    #         number = get_word_number(new_word.feats)
    #         return {"word": original_number, "type": "ADJ", "case": "Nom", "gender": gender,"number": number, "deprel": deprel}

    #  Числительное является подлежащим, необходимо найти число по глаголу.
    if word.deprel == "nsubj" and word.upos == "NUM":
        for new_word in sentence_words:
            if new_word.head == word.id:
                if new_word.upos in ["PROPN", "PRON", "NOUN"]:
                    if has_word(sentence_words, new_word.id, word.id, "из"):
                        return {"word": original_number, "type": word.upos, "case": "Gen", "gender": gender,
                                "number": "Sing", "deprel": deprel}
                    gender = get_word_gender(new_word.feats)
                    case = get_word_case(new_word.feats)
                    if gender == -1:
                        gender = "Masc"
                    return {"word": original_number, "type": word.upos, "case": "Nom", "gender": gender,
                            "number": "Sing", "deprel": deprel}
        if word.head != 0:
            wrd = sentence_words[word.head - 1]
            gender = get_word_gender(wrd.feats)
            number = get_word_number(wrd.feats)
            return {"word": original_number, "type": word.upos, "case": "Nom", "gender": gender, "number": number,
                    "deprel": deprel}
        return {"word": original_number, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing",
                "deprel": deprel}

    # Числительное с опущенным зависимым существительным. Если стоит с наречием - РП, иначе - ИП
    if word.deprel == "nsubj:pass":
        case = "Nom"
        for elem in sentence_words:
            if elem.head == word.id and elem.upos == "ADP":
                case = "Gen"
        return {"word": original_number, "type": word.upos, "case": case, "gender": "Masc", "number": "Sing",
                "deprel": deprel}

    if word.upos == "NUM" and (word.deprel == "root" or re.match("nsubj", word.deprel)):
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
                if new_word.upos in ["NOUN", "PROPN", "PRON"]:
                    numb = get_word_number(new_word.feats)
                    case = get_word_case(new_word.feats)
                    gend = get_word_gender(new_word.feats)
                    for n_word in sentence_words:
                        if n_word.head == word.id and is_numeric(n_word) and n_word.deprel in ["nmod", "amod"]:
                            numb = "Sing"

                    if new_word.lemma == "раз":
                        for raz_word in sentence_words:
                            if raz_word.head == new_word.id and raz_word.upos == "ADP":
                                return {"word": original_number, "type": "ADJ", "case": "Acc", "gender": "Masc",
                                        "number": "Sing",
                                        "deprel": deprel}
                        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend, "number": numb,
                                "deprel": deprel}

                    if has_word(sentence_words, word.id, new_word.id, "из"):
                        numb = "Sing"
                        for n_word in sentence_words:
                            if n_word.lemma == "из" and n_word.head == word.id:
                                if n_word.id > word.id:
                                    return {"word": original_number, "type": "ADJ", "case": case, "gender": gend,
                                            "number": "Sing",
                                            "deprel": deprel}

                    for n_word in sentence_words:
                        if n_word.head == word.id and n_word.upos == "ADP":
                            f1 = get_case_by_adp(n_word.lemma)
                            if f1 != -1:
                                case = f1
                                return {"word": original_number, "type": "NUM", "case": case, "gender": gend,
                                        "number": numb,
                                        "deprel": deprel}
                    cas = -1
                    for adp in sentence_words:
                        if adp.head == word.id and adp.upos == "ADP":
                            cas = get_case_by_adp(adp.text)
                    if cas != -1:
                        case = cas

                    # if case == ["Dat", "Loc", "Ins"]:
                    #     if original_number != "1":
                    #         if case == "Plur":
                    #             return {"word": original_number, "type": "NUM", "case": case, "gender": gend,
                    #                     "number": numb, "deprel": deprel}
                    #     else:
                    #         return {"word": original_number, "type": "NUM", "case": case, "gender": gend,
                    #                 "number": numb, "deprel": deprel}

                    if case == "Ins":
                        return {"word": original_number, "type": "NUM", "case": "Ins", "gender": gend, "number": numb,
                                "deprel": deprel}

                    if case == "Loc":
                        if numb == "Plur" or original_number == "1":
                            return {"word": original_number, "type": "NUM", "case": "Loc", "gender": gend,
                                    "number": numb,
                                    "deprel": deprel}
                        return {"word": original_number, "type": "ADJ", "case": "Loc", "gender": gend, "number": numb,
                                "deprel": deprel}

                    if case == "Dat":
                        return {"word": original_number, "type": "NUM", "case": "Dat", "gender": gend, "number": numb,
                                "deprel": deprel}

                    if case == "Gen":
                        if new_word.deprel == "nmod":
                            if numb == "Plur" or original_number == "1":
                                return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend,
                                        "number": "Plur",
                                        "deprel": deprel}
                            else:
                                return {"word": original_number, "type": "ADJ", "case": "Gen", "gender": gend,
                                        "number": "Sing",
                                        "deprel": deprel}

                        if new_word.deprel == "obl":
                            if original_number == "1":
                                return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend,
                                        "number": "Sing",
                                        "deprel": deprel}
                            else:
                                if numb == "Plur":
                                    return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend,
                                            "number": "Sing",
                                            "deprel": deprel}
                                else:
                                    return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend,
                                            "number": "Sing",
                                            "deprel": deprel}
                                # ADJ???????

                        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend, "number": numb,
                                "deprel": deprel}

                    if case in ["Acc", "Nom"]:
                        if original_number == "1":
                            return {"word": original_number, "type": "NUM", "case": case, "gender": gend,
                                    "number": numb,
                                    "deprel": deprel}
                        return {"word": original_number, "type": "ADJ", "case": case, "gender": gend, "number": numb,
                                "deprel": deprel}

                    if new_word.deprel == "nsubj":
                        if original_number == "1":
                            return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend,
                                    "number": numb,
                                    "deprel": deprel}
                        else:
                            return {"word": original_number, "type": "ADJ", "case": "Nom", "gender": gend,
                                    "number": numb,
                                    "deprel": deprel}

                    if new_word.deprel in ["nsubj", "obl"] or new_word.upos not in ["NOUN", "PRON", "PROPN"]:
                        case = "Nom"
                    if case != -1:
                        if numb == "Plur":
                            return {"word": original_number, "type": word.upos, "case": case, "gender": "Masc",
                                    "number": "Plur",
                                    "deprel": deprel}
                        elif gend != -1:
                            return {"word": original_number, "type": word.upos, "case": case, "gender": gend,
                                    "number": "Sing",
                                    "deprel": deprel}
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc",
                "number": "Sing", "deprel": deprel}

    # if re.match("nummod", word.deprel) and word.deprel != "nummod":
    #     new_word = sentence_words[word.head - 1]
    #     numb = get_word_number(new_word.feats)
    #     case = get_word_case(new_word.feats)
    #     gend = get_word_gender(new_word.feats)
    #
    #     if new_word.deprel in ["nsubj", "obl"] or new_word.upos not in ["NOUN", "PRON", "PROPN"]:
    #         case = "Nom"
    #
    #     return {"word": original_number, "type": word.upos, "case": case, "gender": gend, "number": numb, "deprel": deprel}

    if re.match("nummod", word.deprel) or word.deprel == "parataxts":
        new_word = sentence_words[word.head - 1]
        numb = get_word_number(new_word.feats)
        case = get_word_case(new_word.feats)
        gend = get_word_gender(new_word.feats)
        # print(case)

        for n_word in sentence_words:
            if n_word.head == word.id and is_numeric(n_word) and n_word.deprel in ["nmod", "amod"]:
                numb = "Sing"

        if new_word.lemma == "раз":
            for raz_word in sentence_words:
                if raz_word.head == new_word.id and raz_word.upos == "ADP":
                    return {"word": original_number, "type": "ADJ", "case": "Acc", "gender": "Masc", "number": "Sing",
                            "deprel": deprel}
            return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend, "number": numb,
                    "deprel": deprel}

        if has_word(sentence_words, word.id, new_word.id, "из"):
            numb = "Sing"
            for n_word in sentence_words:
                if n_word.lemma == "из" and n_word.head == word.id:
                    if n_word.id > word.id:
                        return {"word": original_number, "type": "ADJ", "case": case, "gender": gend, "number": "Sing",
                                "deprel": deprel}

        for n_word in sentence_words:
            if n_word.head == word.id and n_word.upos == "ADP":
                f1 = get_case_by_adp(n_word.lemma)
                if f1 != -1:
                    case = f1
                    return {"word": original_number, "type": "NUM", "case": case, "gender": gend, "number": numb,
                            "deprel": deprel}
        cas = -1
        for adp in sentence_words:
            if adp.head == word.id and adp.upos == "ADP":
                cas = get_case_by_adp(adp.text)
        if cas != -1:
            case = cas

        # if case == ["Dat", "Loc", "Ins"]:
        #     if original_number != "1":
        #         if case == "Plur":
        #             return {"word": original_number, "type": "NUM", "case": case, "gender": gend,
        #                     "number": numb, "deprel": deprel}
        #     else:
        #         return {"word": original_number, "type": "NUM", "case": case, "gender": gend,
        #                 "number": numb, "deprel": deprel}

        if case == "Ins":

            return {"word": original_number, "type": "NUM", "case": "Ins", "gender": gend, "number": numb,
                    "deprel": deprel}

        if case == "Loc":
            if numb == "Plur" or original_number == "1":
                return {"word": original_number, "type": "NUM", "case": "Loc", "gender": gend, "number": numb,
                        "deprel": deprel}
            return {"word": original_number, "type": "ADJ", "case": "Loc", "gender": gend, "number": numb,
                    "deprel": deprel}

        if case == "Dat":
            return {"word": original_number, "type": "NUM", "case": "Dat", "gender": gend, "number": numb,
                    "deprel": deprel}

        if case == "Gen":
            if new_word.deprel == "nmod":
                if numb == "Plur" or original_number == "1":
                    return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend, "number": "Plur",
                            "deprel": deprel}
                else:
                    return {"word": original_number, "type": "ADJ", "case": "Gen", "gender": gend, "number": "Sing",
                            "deprel": deprel}

            if new_word.deprel == "obl":
                if original_number == "1":
                    return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend, "number": "Sing",
                                "deprel": deprel}
                else:
                    if numb == "Plur":
                        return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gend, "number": "Sing",
                                "deprel": deprel}
                    else:
                        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend, "number": "Sing",
                                "deprel": deprel}
                    # ADJ???????

            return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend, "number": numb,
                    "deprel": deprel}

        if case in ["Acc", "Nom"]:
            if original_number == "1":
                return {"word": original_number, "type": "NUM", "case": case, "gender": gend, "number": numb,
                        "deprel": deprel}
            return {"word": original_number, "type": "ADJ", "case": case, "gender": gend, "number": numb,
                    "deprel": deprel}

        if new_word.deprel == "nsubj":
            if original_number == "1":
                return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gend, "number": numb,
                        "deprel": deprel}
            else:
                return {"word": original_number, "type": "ADJ", "case": "Nom", "gender": gend, "number": numb,
                        "deprel": deprel}

        if new_word.deprel in ["nsubj", "obl"] or new_word.upos not in ["NOUN", "PRON", "PROPN"]:
            case = "Nom"
        if case != -1:
            if numb == "Plur":
                return {"word": original_number, "type": word.upos, "case": case, "gender": "Masc", "number": "Plur",
                        "deprel": deprel}
            elif gend != -1:
                return {"word": original_number, "type": word.upos, "case": case, "gender": gend, "number": "Sing",
                        "deprel": deprel}

    # Числительное как приложение
    if word.deprel == "appos":
        return {"word": original_number, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing",
                "deprel": deprel}

    # Числительное - дополнение
    if word.upos == "NUM" and word.deprel == "nmod":
        # Если оно зависит от другого числительного
        if is_numeric(sentence_words[word.head - 1]):
            return process_num(sentence_words[word.head - 1], s, deprel, original_number)

        if word.id != 1 and sentence_words[word.id - 2].lemma == "из":
            return {"word": original_number, "type": "ADJ", "case": "Gen", "gender": "Masc", "number": "Plur",
                    "deprel": deprel}

        if has_word(sentence_words, word.head, word.id, "из"):
            return {"word": original_number, "type": "NUM", "case": "Gen", "gender": "Masc", "number": "Sing",
                    "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "parataxis":
        for wrd in sentence_words:
            if wrd.head == word.id:
                if wrd.deprel == "flat":
                    f = get_params(wrd.feats)
                    if f != -1:
                        return {"word": original_number, "type": "ADJ", "case": f[0], "gender": f[1], "number": f[2],
                                "deprel": deprel}
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc", "number": "Sing",
                "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "obl":
        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos in ["NOUN", "PRON", "PROPN"]:
                if new_word.upos == "flat":
                    f = get_params(new_word.feats)
                    if f != -1:
                        return {"word": original_number, "type": "ADJ", "case": f[0], "gender": f[1], "number": f[2],
                                "deprel": deprel}

        for new_word in sentence_words:
            if new_word.head == word.id and new_word.upos in ["NOUN", "PRON", "PROPN"]:
                gen = get_word_gender(new_word.feats)
                case = get_word_case(new_word.feats)
                num = get_word_number(new_word.feats)
                if has_word(sentence_words, new_word.id, word.id, "из"):
                    # return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gen, "number": "Sing",
                    #         "deprel": deprel}
                    num = "Sing"
                if case == -1:
                    case = "Nom"
                if num == "Plur":
                    return {"word": original_number, "type": "NUM", "case": case, "gender": "Masc", "number": "Plur",
                            "deprel": deprel}
                if gen != -1:
                    gen = "Masc"
                return {"word": original_number, "type": "NUM", "case": case, "gender": gen, "number": "Sing",
                        "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "compound":
        if is_numeric(sentence_words[word.head - 1]):
            return process_num(sentence_words[word.head - 1], s, deprel, original_number)

    if word.upos == "NUM" and word.deprel == "flat":
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc", "number": "Sing",
                "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "acl":
        num = get_word_number(sentence_words[word.head - 1].feats)
        if num == "Plur":
            return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc", "number": "Plur",
                    "deprel": deprel}
        gen = get_word_gender(sentence_words[word.head - 1].feats)
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gen, "number": "Sing",
                "deprel": deprel}

    if word.upos == "NUM" and word.deprel == "advcl":
        for new_word in sentence_words:
            if new_word.head == word.id:
                num = get_word_number(new_word.feats)
                if num == "Plur":
                    return {"word": original_number, "type": "NUM", "case": "Nom", "gender": "Masc", "number": "Plur",
                            "deprel": deprel}
                gen = get_word_gender(new_word.feats)
                return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gen, "number": "Sing",
                        "deprel": deprel}

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
                    return {"word": original_number, "type": "NUM", "case": "Gen", "gender": gen, "number": num,
                            "deprel": deprel}
                elif new_word.upos in ["PROPN", "NOUN"]:
                    num = get_word_number(new_word.feats)
                    gen = get_word_gender(new_word.feats)
        return {"word": original_number, "type": "NUM", "case": "Nom", "gender": gen, "number": num, "deprel": deprel}

    if word.deprel == "orphan":
        for new_word in sentence_words:
            if (new_word.upos == "NUM" or new_word.upos == "ADJ") and contains_num(new_word.text):
                return process_num(new_word, s, new_word.deprel, original_number)

    return {"word": original_number, "type": word.upos, "case": "Nom", "gender": "Masc", "number": "Sing",
            "deprel": deprel, "flag": "1"}


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

    # with open(filename, "r", encoding="utf-8") as file:
    #     texts = file.read().split("\n")

    texts = ["""Во 2 части фильма."""]
    dictionary = dict()
    start = perf_counter()
    for line in texts:
        doc = nlp(line)
        deplacy.render(doc)
        for sentence in doc.sentences:
            dictionary[sentence.text] = process_sentence(sentence)

    print(f"Time spent: {perf_counter() - start}")
    print(json.dumps(dictionary, ensure_ascii=False))
    with open("t.json", "w", encoding="utf-8") as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
