# AI Predictive

## Testes Locais

### Pipeline de Treinamento
Execute o script de treinamento:
```bash
python ../../train/train_prophet.py
```
Verifique se o modelo foi salvo em `models/`.

### Teste de Endpoint
Utilize o teste automatizado:
```bash
pytest ../../tests/test_ai_predictive.py
```
Ou manualmente via curl:
```bash
curl -X POST http://localhost:8010/api/predict-seasonal-demand -H "Content-Type: application/json" -d '{"product_category": "electronics", "keywords": ["smartphone"]}'
```

### Integração
Verifique se o serviço está acessando dados e modelos corretamente e se conecta ao PostgreSQL.

---

## Resultados
- Modelo treinado salvo com sucesso.
- Endpoint responde corretamente.
- Integração com banco e dados validada.

---

Repita os testes para cada serviço/módulo conforme exemplos abaixo.
