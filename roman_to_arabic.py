from roman_arabic_numerals import conv

# Словарь для перевода римских цифр в арабские числ
dict_roman_to_arabic = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000
}


def convert(number):
    """Перевод римского числа в арабскую форму
    :param str number: римское число, записанное заглавными латинскими буквами из алфавита I, V, X, L, C, D, M"""

    # Если number - пустая строка, то возвращается 0, необходимо для рекурсивной работы алгоритма
    if number == "":
        return 0

    # Поиск индексов последовательности самых больших цифр в числе
    biggest_index_begin = 0
    biggest_index_end = 1
    flag_sequence = True
    for letter_index in range(1, len(number)):
        letter = number[letter_index]
        if letter not in dict_roman_to_arabic.keys():
            raise Exception(f"Входной параметр number не является римским числом. '{letter}' - не римское число!")

        if dict_roman_to_arabic[letter] > dict_roman_to_arabic[number[biggest_index_begin]]:
            biggest_index_begin = letter_index
            biggest_index_end = letter_index
            flag_sequence = True
        if number[biggest_index_begin] == letter:
            if flag_sequence:
                biggest_index_end += 1
        else:
            flag_sequence = False

    # Рассмотрение случая, когда число number записано одной и той же цифрой целиком.
    if biggest_index_begin == 0 and biggest_index_end == len(number):
        return dict_roman_to_arabic[number[0]] * biggest_index_end

    # Если число записано более чем одной цифрой, то максимальная цифра умножается на их количество и вычитается
    return dict_roman_to_arabic[number[biggest_index_begin]] * (biggest_index_end - biggest_index_begin) \
        - convert(number[:biggest_index_begin]) \
        + convert(number[biggest_index_end:])


if __name__ == "__main__":
    print("Тестирование работы переводчика")

    while True:
        s = str(input(": "))
        if s == "":
            break
        print(f"Результат: {convert(s)}; roman_arabic_numerals: {conv.rom_arab(s)}")

    for i in range(10000):
        ali = conv.arab_rom(i)
        mine = convert(ali)
        if i != mine:
            print(i, ali, mine)
