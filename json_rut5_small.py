import json

f = open('rut5small.json')
data = json.load(f)
eval = []
loss = []
for i in data:
    try:
        a = i["eval_loss"]
        eval.append(float(a))
    except:
        a = i["loss"]
        loss.append(float(a))

print(f"{eval}\n{loss}")
f.close()