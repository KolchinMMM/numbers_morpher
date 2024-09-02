
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline

import csv


def answer(x, **kwargs):
    inputs = tokenizer(x, return_tensors='pt').to(model.device)
    with torch.no_grad():
        hypotheses = model.generate(**inputs, **kwargs, max_length=300)
    return tokenizer.decode(hypotheses[0], skip_special_tokens=True)


raw_model = "float2600"
model = T5ForConditionalGeneration.from_pretrained(raw_model)
tokenizer = T5Tokenizer.from_pretrained(raw_model)

file = open("results.csv", "w", encoding="utf-8", newline="")

writer = csv.writer(file)

writer.writerow(["q", "a"])


pipe = pipeline('text2text-generation', model=model, tokenizer=tokenizer, max_length=512)

with open("main.txt", "r", encoding="utf-8") as f:
    text = f.read().split("\n")

for sentence in text:
    generated = pipe(sentence)
    print(generated)
    writer.writerow([sentence, generated])
