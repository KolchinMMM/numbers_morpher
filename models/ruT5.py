import pandas as pd
import numpy as np
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import random
from tqdm.auto import tqdm, trange
import os
from sklearn.model_selection import train_test_split
import time
from transformers import EarlyStoppingCallback
from transformers import BertForSequenceClassification, Trainer, TrainingArguments
from transformers import Seq2SeqTrainingArguments, DataCollatorForSeq2Seq, Seq2SeqTrainer
import torchtext as tt
from datasets import load_dataset
import evaluate
from sklearn import metrics
from sklearn.metrics import classification_report
from transformers import pipeline

import compare


raw_model = 'ai-forever/ruT5-large'
model = T5ForConditionalGeneration.from_pretrained(raw_model).cuda()
tokenizer = T5Tokenizer.from_pretrained(raw_model, legacy=False)

start = time.perf_counter()


# def compute_metrics(eval_pred):
#     logits, labels = eval_pred
#     predictions = np.argmax(logits, axis=-1)
#     return metric.compute(predictions=predictions, references=labels)

# def compute_metrics(pred):
#     labels = pred.label_ids
#     preds = pred.predictions.argmax(-1)
#     precision, recall, f1, _ = metrics.precision_recall_fscore_support(labels, preds, average='micro')
#     acc = metrics.accuracy_score(labels, preds)
#     return {
#         'accuracy': acc,
#         'f1': f1,
#         'precision': precision,
#         'recall': recall
#     }


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    print(classification_report(labels, predictions))
    return metric.compute(predictions=predictions, references=labels)


def preprocess(examples):
    model_inputs = tokenizer(examples['q'], truncation=True, padding=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples['a'], truncation=True, padding=True)
    model_inputs['labels'] = labels['input_ids']
    return model_inputs


def answer(x, **kwargs):
    inputs = tokenizer(x, return_tensors='pt').to(model.device)
    with torch.no_grad():
        hypotheses = model.generate(**inputs, **kwargs, max_length=100)
    return tokenizer.decode(hypotheses[0], skip_special_tokens=True)


optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)

data_files = {"train": "d/test10000.csv", "test": "d/train1000.csv"}

dataset = load_dataset("csv", data_files=data_files, encoding="utf-8")

data_train = dataset["train"].map(preprocess, batched=False)
data_train = data_train.remove_columns(dataset["train"].column_names)

data_test = dataset["test"].map(preprocess, batched=True)
data_test = data_test.remove_columns(dataset["test"].column_names)


model.train()
losses = []

metric = evaluate.load("accuracy")

training_args = TrainingArguments(
    output_dir='./results',  # output directory
    overwrite_output_dir=True,
    num_train_epochs=100,  # total # of training epochs
    per_device_train_batch_size=2,  # batch size per device during training
    per_device_eval_batch_size=2,  # batch size for evaluation
    warmup_steps=0,  # number of warmup steps for learning rate scheduler
    weight_decay=0.01,  # strength of weight decay
    logging_dir='./logs',  # directory for storing logs
    remove_unused_columns=False,
    logging_strategy="epoch",
    metric_for_best_model='eval_loss',
    evaluation_strategy='epoch',
    save_strategy="epoch",
    load_best_model_at_end=True,
    # do_train=True,
    # do_eval=True,
    save_total_limit=6,
    no_cuda=False,
)

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=data_test,
    eval_dataset=data_test,
    data_collator=data_collator,
    tokenizer=tokenizer,
    # compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
)

trainer.train()
trainer.save_model(f"float2600")

print("\nВремя обучения: ", time.perf_counter() - start)
trainer.save_model("model_100k")
# trainer.evaluate()
#
# trainer.predict(data_val)
# torch.cuda.empty_cache()
# trainer.evaluate(eval_dataset=data_test)
