from mediawiki import MediaWiki
import time
import words2numsrus
import razdel
import json


def contains_num(s):
    return any(i.isdigit() for i in s)


a = words2numsrus.NumberExtractor()


wikipedia = MediaWiki(url="https://ru.wikipedia.org/w/api.php")
s = time.time()

count = 0
index = 12
d = dict()
big_d = dict()
while True:
    page_title = wikipedia.random()
    try:
        page = wikipedia.page(page_title)
        for sentence1 in razdel.sentenize(page.content):
            for sentence in sentence1.text.split("\n"):
                changed = a.replace_groups(sentence)
                if changed != sentence and not contains_num(sentence):
                    if sentence not in big_d.keys():
                        print(count)
                        print(f"before: \n{sentence}\nafter: \n{changed}")
                        count += 1
                        d[sentence] = changed
                        big_d[sentence] = changed
                        if count // 10000 == 1:
                            count = 0
                            index += 1
                            with open(f"dir/{index}.json", "w", encoding="utf-8") as file:
                                json.dump(d, file, ensure_ascii=False, indent=4)
                            d = dict()
    except:
        pass


print(f"Time spent: {time.time()-s}")