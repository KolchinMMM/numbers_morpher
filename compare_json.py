import json


filepath_right = "right.json"
filepath = "text.json"

with open(filepath_right, "r", encoding="utf-8") as file:
    correct = json.load(file)
for i in correct:
    print(json.dumps(i, indent=4))
