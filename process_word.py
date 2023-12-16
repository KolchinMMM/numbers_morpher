from num2words import num2words
from roman_arabic_numerals import conv
from pymorphy3 import MorphAnalyzer


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

    case = dict_stanza_to_pymorphy[case]
    # Если число не порядковое, то оно всегда в единственном числе, иначе - ошибка

    # if form not in dict_forms.keys():
    #     raise AttributeError("Неверная форма числительного. Допускаются: sing, plur, femn, masc")
    # if not is_ordinal and form == "plur":
    #     raise AttributeError("Не порядковое числительное всегда в единственном числе (sing)")

    if numb == "Plur":
        form="plur"
    elif gender == "Masc":
        form = "masc"
    else:
        form = "femn"


    if tp == "NUM":
        is_ordinal = False
    else:
        is_ordinal = True

    if case not in dict_cases.keys():
        print(case)
        raise AttributeError("Неверный падеж")

    # Замена римского числа
    if not str(num).isdigit():
        num = conv.rom_arab(num)
        # Если число введено неправильно
        if not str(num).isdigit():
            raise AttributeError("Неверное значение числа")

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
            new_word += wrd_morph.inflect({case}).word + " "
        new_word = new_word.lstrip(' ')

    print(f"{num}: {new_word}")
    return new_word
