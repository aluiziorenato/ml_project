from transformers import BertTokenizer, BertForSequenceClassification
import lime
import lime.lime_text
import torch
import os

def explain_intent(text, model_dir="../models/intent_model"):
    tokenizer = BertTokenizer.from_pretrained(model_dir)
    model = BertForSequenceClassification.from_pretrained(model_dir)
    model.eval()
    class_names = ["comprar", "cancelar", "reclamar", "tirar dúvida"]
    explainer = lime.lime_text.LimeTextExplainer(class_names=class_names)
    def predict_proba(texts):
        inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        return probs.numpy()
    exp = explainer.explain_instance(text, predict_proba, num_features=6)
    return exp.as_list()
