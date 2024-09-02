import pandas as pd
import numpy as np
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, T5Config, GPT2Tokenizer, GPT2Config, GPT2Model, \
    AutoModel, AutoTokenizer, AutoConfig, GPT2LMHeadModel
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
import random
import tqdm
import json
import os
from sklearn.model_selection import train_test_split
import time
from transformers import EarlyStoppingCallback, BartForConditionalGeneration, TFGPT2Model, ByT5Tokenizer
from transformers import BertForSequenceClassification, Trainer, TrainingArguments, GPT2ForSequenceClassification, \
    GPT2DoubleHeadsModel, BertForSequenceClassification
from transformers import Seq2SeqTrainingArguments, DataCollatorForSeq2Seq, Seq2SeqTrainer, \
    DataCollatorForLanguageModeling, DataCollatorWithPadding, AutoModelForCausalLM, AutoModelForSeq2SeqLM, \
    TFGPT2LMHeadModel, GPT2ForQuestionAnswering
import torchtext as tt
from datasets import load_dataset
import evaluate
from sklearn import metrics
from sklearn.metrics import classification_report
from transformers import pipeline
from safetensors.torch import load_model, save_model
import compare
from torch.utils.data import Dataset, DataLoader
import csv


class FinetuneDataset(Dataset):
    def __init__(self, samples, tokenizer):
        self.tokenizer = tokenizer
        self.max_input_len = 0
        self.max_output_len = 0
        self.samples = []

        self.bos_token_id = tokenizer.encode('<s>', add_special_tokens=False)[0]
        self.eos_token_id = tokenizer.encode('</s>', add_special_tokens=False)[0]
        self.pad_token_id = tokenizer.encode('<pad>', add_special_tokens=False)[0]

        for sample in samples:
            input_ids = sample['input_tokens']
            output_ids = sample['output_tokens'] + [self.eos_token_id]
            self.samples.append((input_ids, output_ids))
            self.max_input_len = max(self.max_input_len, len(input_ids))
            self.max_output_len = max(self.max_output_len, len(output_ids))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index: int):
        input_ids, output_ids = self.samples[index]

        input_npad = self.max_input_len - len(input_ids)
        attention_mask = [1] * len(input_ids) + [0] * input_npad
        input_ids = input_ids + input_npad * [self.pad_token_id]

        output_npad = self.max_output_len - len(output_ids)
        labels = output_ids + output_npad * [-100]

        return {'input_ids': torch.LongTensor(input_ids),
                'attention_mask': attention_mask,
                'labels': torch.LongTensor(labels),
                }


def load_samples(dataset_path, tokenizer):
    samples = []
    text = []
    with open(dataset_path, 'r') as f:
        csv_reader = csv.DictReader(f, delimiter=',')
        count = 0
        for row in csv_reader:
            if count != 0:
                text.append([row["q"], row["a"]])
            count += 1
        for sample in tqdm.tqdm(json.load(f)):
            try:
                seed = '<SC1>' + sample[0] + '<extra_id_0>'
                reply = '<extra_id_0>' + sample[1]
                input_tokens = tokenizer.encode(seed, add_special_tokens=False, truncation=True, max_length=1024)
                output_tokens = tokenizer.encode(reply, add_special_tokens=False)  # , truncation=True, max_length=1024)
                if len(input_tokens) < 768 and len(output_tokens) < 768:  # пока ограничим многословность
                    samples.append({'input_tokens': input_tokens,
                                    'output_tokens': output_tokens,
                                    'seed': seed,
                                    'reply': reply})

            except Exception as ex:
                print(ex)

    return samples


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
    model_inputs = tokenizer(examples['q'], padding="max_length", max_length=100, truncation=True, return_tensors="tf")
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples['a'], padding="max_length", max_length=100, truncation=True, return_tensors="tf")
    model_inputs['labels'] = labels['input_ids']

    return model_inputs


def prepare_validation_features(dataset):
    tokenized_examples = []
    for example in dataset:
        tokenized_example = tokenizer.encode(example, return_tensors="pt").squeeze()
        tokenized_examples.append(tokenized_example)
    return {"input_ids": tokenized_examples, "label": dataset["label"]}


def answer(x, **kwargs):
    inputs = tokenizer(x, return_tensors='pt').to(model.device)
    with torch.no_grad():
        hypotheses = model.generate(**inputs, **kwargs)
    return tokenizer.decode(hypotheses[0], skip_special_tokens=True)


# cointegrated/rut5-base-multitask
# ai-forever/ruT5-large
# ai-forever/rugpt3medium_based_on_gpt2
# ai-forever/FRED-T5-1.7B
# gurgutan/ruGPT-13B-4bit
# fffrrt/ruGPT-3.5-13B-GPTQ

raw_model = 'ai-forever/rugpt3small_based_on_gpt2'

model = GPT2LMHeadModel.from_pretrained(raw_model)
tokenizer = GPT2Tokenizer.from_pretrained(raw_model, legacy=False)
model.to("cuda")
start = time.perf_counter()


optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)

data_files = {"train": "d/train10000.csv", "test": "d/test1000.csv"}

dataset = load_dataset("csv", data_files=data_files, encoding="utf-8")

btch = 1

# data_train = load_samples(data_files["train"], tokenizer)
# data_train = FinetuneDataset(data_train, tokenizer)
#
# data_test = load_samples(data_files["test"], tokenizer)
# data_test = FinetuneDataset(data_test, tokenizer)

data_train = dataset["train"].map(preprocess, batched=True, batch_size=btch)
data_train = data_train.remove_columns(dataset["train"].column_names)

data_test = dataset["test"].map(preprocess, batched=True, batch_size=btch)
data_test = data_test.remove_columns(dataset["test"].column_names)

model.train()
losses = []

metric = evaluate.load("accuracy")

training_args = TrainingArguments(
    output_dir='./resultsgpt3_5',  # output directory
    save_safetensors=True,
    overwrite_output_dir=True,
    num_train_epochs=100,  # total # of training epochs
    per_device_train_batch_size=btch,  # batch size per device during training
    per_device_eval_batch_size=btch,  # batch size for evaluation
    warmup_steps=0,  # number of warmup steps for learning rate scheduler
    weight_decay=0.01,  # strength of weight decay
    logging_dir='./logs',  # directory for storing logs
    remove_unused_columns=False,
    logging_strategy="epoch",
    metric_for_best_model='eval_loss',
    evaluation_strategy='epoch',
    save_strategy="epoch",
    load_best_model_at_end=True,
    do_train=True,
    do_eval=True,
    save_total_limit=6,
    no_cuda=False,
    # report_to="tensorboard"
)

data_collator = DataCollatorWithPadding(tokenizer, padding="max_length", max_length=300)
# data_collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding="max_length", max_length=300)
# data_collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding="max_length", max_length=300, return_tensors="pt")

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=data_train,
    eval_dataset=data_test,
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
)

trainer.train()
print("\nВремя обучения: ", time.perf_counter() - start)
save_model(model, "googlesmall.safetensors")
trainer.save_model("googlesmall.safetensors")
# trainer.evaluate()
#
# trainer.predict(data_val)

# pipel = pipeline(model=model, tokenizer=tokenizer)

file = pd.read_csv("d/validate.csv")
count_right = 0
count_all = 0
count_right_sentence = 0
count_all_sentence = 0
for struct in file.values:
    # print(struct[0])
    ans = answer(struct[0])
    # input_ids = tokenizer(struct[0], return_tensors="pt").to(model.device).input_ids
    # outputs = model.generate(input_ids, max_length=100)
    # print(tokenizer.decode(outputs[0], skip_special_tokens=True))
    c_right, c_all = compare.compare(struct[1], ans)
    count_right += c_right
    count_all += c_all
    if ans == struct[1]:
        count_right_sentence += 1
    count_all_sentence += 1

print(
    f"accuracy(предложения): {count_right_sentence / count_all_sentence}({count_right_sentence}/{count_all_sentence})")
print(f"accuracy(слова): {count_right / count_all}({count_right}/{count_all})")

# torch.cuda.empty_cache()
# trainer.evaluate(eval_dataset=data_test)
