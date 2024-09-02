import pandas as pd
import numpy as np
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline
import random
from tqdm.auto import tqdm, trange
import os
from sklearn.model_selection import train_test_split
import time


def answer(x, **kwargs):
    inputs = tokenizer(x, return_tensors='pt').to(model.device)
    with torch.no_grad():
        hypotheses = model.generate(**inputs, **kwargs, max_length=300)
    return tokenizer.decode(hypotheses[0], skip_special_tokens=True)


raw_model = "model_gpt3_5.safetensors"
model = T5ForConditionalGeneration.from_pretrained(raw_model).cuda()
tokenizer = T5Tokenizer.from_pretrained(raw_model)


pipe = pipeline('text2text-generation', model=model, tokenizer=tokenizer, max_length=512)
print(pipe("1 мировая война."))