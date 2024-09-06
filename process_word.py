from num2words import num2words
from roman_arabic_numerals import conv
from pymorphy3 import MorphAnalyzer
import re

def contains_num(s):
    return any(i.isdigit() for i in s)

morph = MorphAnalyzer()

dict_cases = {
    "nomn": "именительный",
    "gent": "родительный",
    "datv": "дательный",
    "accs": "винительный",
    "ablt": "творительный",
    "loct": "предложный",
    "voct": "звательный",
    "gen2": "второй родительный",
    "acc2": "второй винительный",
    "loc2": "второй предложный"
}

dict_forms = {
    "femn": "мужской род",
    "masc": "женский род",
    "sing": "единственное число",
    "plur": "множественное число"
}

dict_stanza_to_pymorphy = {
    "Nom": 'nomn',
    "Gen": 'gent',
    "Dat": 'datv',
    "Acc": 'accs',
    "Ins": 'ablt',
    "Loc": 'loct'
}


def switch_case(num, case, gender, numb, tp="NUM"):
    """ Преобразует число в нужную форму.
    num - str или int, является числом, которое нужно преобразовать,
    case - падеж, form - форма числительного, может быть masc, femn, sing, plur. is_ordinal - является ли порядковым"""
    # print(f"switch case: {num, case, gender, numb, tp}")
    for symbol in "—–−-":
        if symbol in num:
            t = num.split(symbol)
            if contains_num("".join(t[1:])) and contains_num(t[0]):
                return switch_case(t[0], case, gender, numb, tp) + symbol + switch_case("".join(t[1:]), case, gender, numb, tp)
            else:
                num = t[0]
                break
    if len(re.findall("[^0-9]", num)) > 1:
        return
    num = num.replace(",", ".")
    case = dict_stanza_to_pymorphy[case]
    # Если число не порядковое, то оно всегда в единственном числе, иначе - ошибка

    # if form not in dict_forms.keys():
    #     raise AttributeError("Неверная форма числительного. Допускаются: sing, plur, femn, masc")
    # if not is_ordinal and form == "plur":
    #     raise AttributeError("Не порядковое числительное всегда в единственном числе (sing)")
    if gender == -1:
        gender = "Masc"
    if numb == -1:
        numb = "Sing"

    if numb == "Plur":
        form = "plur"
    elif gender == "Masc":
        form = "masc"
    elif gender == "Fem":
        form = "femn"
    else:
        form = gender.lower()

    if tp == "NUM":
        is_ordinal = False
    else:
        is_ordinal = True

    if case not in dict_cases.keys():
        raise AttributeError("Неверный падеж")

    # # Замена римского числа
    # if not str(num).isdigit():
    #     num = conv.rom_arab(num)
    #     # Если число введено неправильно
    #     if not str(num).isdigit():
    #         raise AttributeError("Неверное значение числа")

    if "." in str(num):

        num_word = num2words(num, lang="ru")
        split_word = num_word.split(' ')
        to_return = []
        for word in split_word:
            if word[-2:] == "ых":
                to_return.append(word)
            else:
                w = morph.parse(word)[0]
                wr = w.inflect({case}).word
                to_return.append(wr)
        return ' '.join(to_return)
    num_word = num2words(num, lang="ru", ordinal=is_ordinal)
    split_word = num_word.split(' ')
    new_word = ""

    # Если числительное порядковое
    if is_ordinal:
        last = morph.parse(split_word[-1])[0]
        if len(split_word) == 1:
            new_word = last.inflect({case, form}).word
        else:
            new_word = ' '.join(split_word[:-1:]) + " " + last.inflect({case, form}).word
    # Если числительное не порядковое
    else:
        for wrd in split_word:
            wrd_morph = morph.parse(wrd)[0]
            morphed = wrd_morph.inflect({case, form})
            if morphed is None:
                morphed = wrd_morph.inflect({case})
            new_word += morphed.word + " "
        new_word = new_word.lstrip(' ')
    new_word = new_word.strip()
    splitted = new_word.split(" ")
    if len(splitted) >1:
        if splitted[0][:2] == "од":
            return " ".join(splitted[1:])

    return new_word
