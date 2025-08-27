# SEO Intelligence Service

## Testes Locais

### Pipeline de Treinamento
Execute o script de treinamento:
```bash
python ../../train/train_seo_model.py
```
Verifique se o modelo foi salvo em `models/`.

### Teste de Endpoint
Utilize o teste automatizado:
```bash
pytest ../../tests/test_seo_intelligence.py
```
Ou manualmente via curl:
```bash
curl -X POST http://localhost:8040/api/seo-inference -H "Content-Type: application/json" -d '{"url": "https://site.com", "keyword": "otimização"}'
```

### Integração
Verifique se o serviço está acessando dados e modelos corretamente e se conecta ao PostgreSQL.

---

## Resultados
- Modelo treinado salvo com sucesso.
- Endpoint responde corretamente.
- Integração com banco e dados validada.

---

Repita os testes para cada serviço/módulo conforme exemplos acima.

Este serviço realiza inferência de SEO usando modelos de machine learning.

## Endpoints
- `/api/seo-inference`: Recebe URL e palavra-chave, retorna score e recomendações.

## Treinamento do Modelo
- Utilize o script `train/train_seo_model.py` para treinar e salvar o modelo.
- Exemplo de uso:
  ```python
  train_and_save_seo_model("../data/seo_training_data.csv", "../models/seo_model.joblib")
  ```

## Modelos
- Modelos treinados ficam em `models/` (ex: `seo_model.joblib`).

## Exemplo de Dados para Treino
- Estrutura esperada do CSV:
  ```csv
  url,keyword,score
  https://site.com,otimização,0.85
  https://blog.com,seo,0.92
  ```

## Integração
- O endpoint carrega o modelo real salvo em `models/` e realiza predição baseada nos dados enviados.
