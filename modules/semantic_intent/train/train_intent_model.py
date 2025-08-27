from transformers import BertForSequenceClassification, BertTokenizer, Trainer, TrainingArguments
import pandas as pd
import torch
import os
from datetime import datetime

def train_and_save_intent_model(csv_path, model_dir):
    df = pd.read_csv(csv_path)
    texts = df["text"].tolist()
    labels = df["label"].tolist()
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(set(labels)))
    # Pré-processamento e dataset customizado omitidos para exemplo
    # ...
    # Treinamento fictício
    # ...
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model.save_pretrained(f"{model_dir}/intent_model_{timestamp}")
    tokenizer.save_pretrained(f"{model_dir}/intent_model_{timestamp}")
    return f"{model_dir}/intent_model_{timestamp}"

# Exemplo de uso:
# train_and_save_intent_model("../data/intent_training_data.csv", "../models/intent_model")
