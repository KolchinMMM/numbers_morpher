from process_word import switch_case
import re
import json

with open("dir/1.json", encoding="utf-8") as file:
    things = file.read()

d = dict(json.loads(things))

for i, v in d.items():
    print(i, v)
    exit()


