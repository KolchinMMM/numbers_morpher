import stanza
import re
import deplacy
import json


def is_numeric(word):
    """Возвращает, является ли токен слова числительным
    @param: word - Токен синтаксического разбора Stanza"""
    return word.upos in ["NUM", "ADJ"] and contains_num(word.text)


def get_word_case(feats):
    """Возвращает падеж слова, или -1, если его нет
    @params: feats - word.feats, где word - токен синтаксического разбора Stanza"""
    if feats is None:
        return -1
    for feat in feats.split("|"):
        if re.match("Case=", feat):
            return feat[5:]
    return -1


def contains_num(s):
    """Возвращает, содержит ли строка хотя бы одну цифру
    @params: s - строка"""
    return any(i.isdigit() for i in s)


nlp = stanza.Pipeline('ru', use_gpu=True, download_method=False, warnings=True)
# filename = "texts/file_middle.txt"
#
# with open(filename, "r", encoding="utf-8") as file:
#     texts = file.read().split("\n")


def main():
    """Функция для отладки"""
    with open("datasets/dir/1.json", encoding="utf-8") as file:
        things = file.read()

    d = dict(json.loads(things))

    texts = d.values()

    dictishe = dict()
    count = 1
    for se in texts:
        d = nlp(se)
        # deplacy.render(d)
        for s in d.sentences:
            words = s.words
            for word in words:
                if word.lemma == "из":
                    print(s.text)


    dictishe = dict(sorted(dictishe.items(), key=lambda item: item[1]))

    for k, v in dictishe.items():
        print(k, v)


if __name__ == "__main__":
    main()
