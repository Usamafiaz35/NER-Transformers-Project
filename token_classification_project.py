# -*- coding: utf-8 -*-
"""Token classification Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DcEJAf9PuEYzHA0EjJR9Wy6u3pnHg-YL
"""

!pip install datasets

from datasets import load_dataset
raw_datasets = load_dataset("conll2003", trust_remote_code=True)

raw_datasets

raw_datasets["train"][0]["tokens"]

raw_datasets["train"][0]["ner_tags"]

ner_feature = raw_datasets["train"].features["ner_tags"]
ner_feature

label_names = ner_feature.feature.names
label_names

#Decoding the words and aligning with ner_tags
words = raw_datasets["train"][0]["tokens"]
labels = raw_datasets["train"][0]["ner_tags"]
line1 = ""
line2 = ""
for word, label in zip(words, labels):
    full_label = label_names[label]
    max_length = max(len(word), len(full_label))
    line1 += word + " " * (max_length - len(word) + 1)
    line2 += full_label + " " * (max_length - len(full_label) + 1)

print(line1)
print(line2)

from transformers import AutoTokenizer

model_checkpoint = "bert-base-cased"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

tokenizer.is_fast

#Tokenization with pre trained inputs
inputs = tokenizer(raw_datasets["train"][0]["tokens"], is_split_into_words=True)
inputs.tokens()

inputs.word_ids()

# Making a function of converting the Tokens into (input_ids) and alinging with the ner_tags (labels)
def align_labels_with_tokens(labels, word_ids):
    new_labels = []
    current_word = None
    for word_id in word_ids:
        if word_id != current_word:
            # Start of a new word!
            current_word = word_id
            label = -100 if word_id is None else labels[word_id]
            new_labels.append(label)
        elif word_id is None:
            # Special token
            new_labels.append(-100)
        else:
            # Same word as previous token
            label = labels[word_id]
            # If the label is B-XXX we change it to I-XXX
            if label % 2 == 1:
                label += 1
            new_labels.append(label)

    return new_labels

#checking on first sentence , is  our function added the -100 for the two special tokens at the beginning and the end, and a new 0 for our word that was split into two tokens.)
labels = raw_datasets["train"][0]["ner_tags"]
word_ids = inputs.word_ids()
print(labels)
print(align_labels_with_tokens(labels, word_ids))

# Making function to process on Dataset
def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(
        examples["tokens"], truncation=True, is_split_into_words=True
    )
    all_labels = examples["ner_tags"]
    new_labels = []
    for i, labels in enumerate(all_labels):
        word_ids = tokenized_inputs.word_ids(i)
        new_labels.append(align_labels_with_tokens(labels, word_ids))

    tokenized_inputs["labels"] = new_labels
    return tokenized_inputs

tokenized_datasets = raw_datasets.map(
    tokenize_and_align_labels,
    batched=True,
    remove_columns=raw_datasets["train"].column_names,
)

# checking now how data look like
tokenized_datasets

print(tokenized_datasets["train"][0]["input_ids"])
print(tokenized_datasets["train"][0]["token_type_ids"])
print(tokenized_datasets["train"][0]["attention_mask"])
print(tokenized_datasets["train"][0]["labels"])

"""Model Training Start"""

# Normal datacollator not pad the labels , but for this we use (DataCollatorForTokenClassification) for padding labels also woth -100
from transformers import DataCollatorForTokenClassification

data_collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer, return_tensors="tf"
)

# Checking
batch = data_collator([tokenized_datasets["train"][i] for i in range(2)])
batch["labels"]

tf_train_dataset = tokenized_datasets["train"].to_tf_dataset(
    columns=["attention_mask", "input_ids", "labels", "token_type_ids"],
    collate_fn=data_collator,
    shuffle=True,
    batch_size=16,
)

tf_eval_dataset = tokenized_datasets["validation"].to_tf_dataset(
    columns=["attention_mask", "input_ids", "labels", "token_type_ids"],
    collate_fn=data_collator,
    shuffle=False,
    batch_size=16,
)

id2label = {i: label for i, label in enumerate(label_names)}
label2id = {v: k for k, v in id2label.items()}

from transformers import TFAutoModelForTokenClassification

model = TFAutoModelForTokenClassification.from_pretrained(
    model_checkpoint,
    id2label=id2label,
    label2id=label2id,
)

model.config.num_labels

from huggingface_hub import notebook_login

notebook_login()

from transformers import create_optimizer
import tensorflow as tf

tf.keras.mixed_precision.set_global_policy("mixed_float16")

num_epochs = 3
num_train_steps = len(tf_train_dataset) * num_epochs

optimizer, schedule = create_optimizer(
    init_lr=2e-5,
    num_warmup_steps=0,
    num_train_steps=num_train_steps,
    weight_decay_rate=0.01,
)
model.compile(optimizer=optimizer)

from transformers.keras_callbacks import PushToHubCallback

callback = PushToHubCallback(output_dir="bert-finetuned-ner", tokenizer=tokenizer)

model.fit(
    tf_train_dataset,
    validation_data=tf_eval_dataset,
    callbacks=[callback],
    epochs=num_epochs,
)

!pip install seqeval

!pip install evaluate

import evaluate

metric = evaluate.load("seqeval")

labels = raw_datasets["train"][0]["ner_tags"]
labels = [label_names[i] for i in labels]
labels

predictions = labels.copy()
predictions[2] = "O"
metric.compute(predictions=[predictions], references=[labels])

import numpy as np

all_predictions = []
all_labels = []
for batch in tf_eval_dataset:
    logits = model.predict_on_batch(batch)["logits"]
    labels = batch["labels"]
    predictions = np.argmax(logits, axis=-1)
    for prediction, label in zip(predictions, labels):
        for predicted_idx, label_idx in zip(prediction, label):
            if label_idx == -100:
                continue
            all_predictions.append(label_names[predicted_idx])
            all_labels.append(label_names[label_idx])
metric.compute(predictions=[all_predictions], references=[all_labels])

#checking the model

from transformers import pipeline

# Replace this with your own checkpoint
model_checkpoint = "usama35/bert-finetuned-ner"
token_classifier = pipeline(
    "token-classification", model=model_checkpoint, aggregation_strategy="simple"
)
token_classifier("My name is Sylvain and I work at Hugging Face in Brooklyn.")

usama35/bert-finetuned-ner