# ACOS Service

## Testes Locais

### Pipeline de Treinamento
Execute o script de treinamento:
```bash
python ../../train/train_acos_optimizer.py
```
Verifique se o modelo foi salvo em `models/`.

### Teste de Endpoint
Utilize o teste automatizado:
```bash
pytest ../../tests/test_acos_service.py
```
Ou manualmente via curl:
```bash
curl -X POST http://localhost:8020/api/optimize-acos -H "Content-Type: application/json" -d '{"campaign_id": "camp1", "spend": 100, "sales": 500, "target_acos": 0.2}'
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

Este serviço realiza otimização de ACOS (Advertising Cost of Sales) usando modelo de machine learning.

## Endpoints
- `/api/optimize-acos`: Recebe dados de campanha e retorna bid otimizado e ACOS esperado.

## Treinamento do Modelo
- Utilize o script `train/train_acos_optimizer.py` para treinar e salvar o modelo.
- Exemplo de uso:
  ```python
  train_and_save_acos_optimizer("../data/acos_training_data.csv", "../models/acos_optimizer.joblib")
  ```

## Modelos
- Modelos treinados ficam em `models/` (ex: `acos_optimizer.joblib`).

## Integração
- O endpoint carrega o modelo real salvo em `models/` e realiza predição baseada nos dados enviados.

## Exemplo de Dados para Treino
- Estrutura esperada do CSV:
  ```csv
  spend,sales,target_acos,optimized_bid
  100,500,0.2,1.5
  200,800,0.18,2.0
  ```
