import json


filepath_right = "json/right.json"
filepath = "json/text.json"

with open(filepath_right, "r", encoding="utf-8") as file:
    correct = json.load(file)
for i in correct:
    print(json.dumps(i, indent=4))
