# Pipeline SEO otimizado com BLIP + DistilBERT
from transformers import DistilBertTokenizer, DistilBertModel, BlipProcessor, BlipForConditionalGeneration
import torch
from PIL import Image
import requests

# Carregamento único dos modelos
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
distilbert_tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
distilbert_model = DistilBertModel.from_pretrained('distilbert-base-uncased')

# Função para gerar descrição a partir da imagem
def gerar_descricao_imagem(img_path):
    image = Image.open(img_path).convert('RGB')
    inputs = blip_processor(image, return_tensors="pt")
    out = blip_model.generate(**inputs)
    descricao = blip_processor.decode(out[0], skip_special_tokens=True)
    return descricao

# Função para sugerir termos/títulos com DistilBERT
def sugerir_termos(texto, num_termos=5):
    tokens = distilbert_tokenizer.tokenize(texto)
    termos = list(set([t for t in tokens if len(t) > 3]))
    termos_freq = sorted(termos, key=lambda x: tokens.count(x), reverse=True)
    return termos_freq[:num_termos]

# Função para gerar título e descrição final
def gerar_titulo_descricao(termos_escolhidos, descricao_base, max_titulo=65):
    titulo = " ".join(termos_escolhidos)
    if len(titulo) > max_titulo:
        titulo = titulo[:max_titulo].rstrip()
    descricao = f"{titulo}. {descricao_base}"
    return titulo, descricao

# Exemplo de uso
if __name__ == "__main__":
    # Caminho da imagem do produto
    img_path = "produto.jpg"  # Substitua pelo caminho real
    descricao_base = gerar_descricao_imagem(img_path)
    termos_sugeridos = sugerir_termos(descricao_base, num_termos=8)
    print("Termos sugeridos:", termos_sugeridos)
    # Simulação de escolha do usuário
    termos_escolhidos = termos_sugeridos[:5]
    titulo, descricao = gerar_titulo_descricao(termos_escolhidos, descricao_base)
    print("Título otimizado:", titulo)
    print("Descrição otimizada:", descricao)
