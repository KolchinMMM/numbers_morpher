# from stanza_json import process_num, contains_num
# from process_word import switch_case
# import stanza
# import json
# from tqdm.auto import tqdm, trange
# from time import sleep
# import re
#
# import stanza
# import words2numsrus
# from num2words import num2words
# from pymorphy3 import MorphAnalyzer
#
#
# nlp = stanza.Pipeline("ru")
#
# regex = '.*([0-1]?[0-9]|2[0-3]):[0-5][0-9].*'
# # print(re.match(regex, "fhfgh 21:22 ghfhg"))
#
# texts = """Дудоров Б. П. Авиация Балтийского моря в 1912–1917 гг. (по воспоминаниям)
# Взятие Правецкой позиции, отражение турецкой атаки под Араб-Конаком 21 ноября (3 декабря)—23 ноября (5 декабря) 1877 года
# """
#
# # print(re.findall("[0-9]+[—–−-][0-9]+", text))
#
# for text in texts.split("\n"):
#     nlpied = nlp(text)
#     for sentence in nlpied.sentences:
#         for word in sentence.words:
#             print(word)


while True:
    s = str(input())
    for i in s.split(", "):
        print(i.replace(',', '').replace('.', ","))