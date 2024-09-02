import wikipedia
import time
import words2numsrus
import razdel
import json
import stanza
import warnings
import re

warnings.catch_warnings()

warnings.simplefilter("ignore")
def contains_num(s):
    return any(i.isdigit() for i in s)


wikipedia.set_lang("ru")
a = words2numsrus.NumberExtractor()

s = time.time()

count = 0
index = 1
d = dict()
big_d = dict()
re_float = ',*[0-9]+[—–−-]+[0-9].*'
re_float_time = '.*([0-1]?[0-9]|2[0-3]):[0-5][0-9].*'
re_date = '[0-3][0-9][./][0-1][0-9][./][0-9]{4}'
f = open("times/date3.txt", "w", encoding="utf-8")
while True:
    page_title = wikipedia.random()
    try:
        page = wikipedia.page(page_title)
        for sentence1 in razdel.sentenize(page.content):
            for sentence in sentence1.text.split("\n"):
                newer = a.replace_groups(sentence)
                if "ISBN" not in sentence and re.findall(re_date, newer):
                    print(sentence)

                    f.write(sentence+"\n")

    except:
        pass
    #             changed = a.replace_groups(sentence)
    #             if changed != sentence and not contains_num(sentence):
    #                 if sentence not in big_d.keys():
    #                     print(count)
    #                     print(f"before: \n{sentence}\nafter: \n{changed}")
    #                     count += 1
    #                     d[sentence] = changed
    #                     big_d[sentence] = changed
    #                     if count // 1000 == 1:
    #                         count = 0
    #                         index += 1
    #                         with open(f"dir2/{index}.json", "w", encoding="utf-8") as file:
    #                             json.dump(d, file, ensure_ascii=False, indent=4)
    #                             print("ahui")
    #                         d = dict()
    # except:
    #     pass

