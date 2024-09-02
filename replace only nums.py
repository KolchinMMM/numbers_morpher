import pandas as pd
from num2words import num2words
import csv
import re

file = pd.read_csv("big_time.csv")
to_write = open("big_time_final.csv", "w", newline='', encoding="utf-8")
writer = csv.writer(to_write)
writer.writerow(["q", "a"])
for i in file.values:
    new_sentence = i[1]
    for match in re.findall('[0-9]+', new_sentence):
        new_sentence = new_sentence.replace(match, num2words(match, lang="ru"))
    writer.writerow([i[0], new_sentence])

to_write.close()