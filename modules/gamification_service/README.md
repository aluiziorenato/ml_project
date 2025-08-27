# Gamification Service

## Testes Locais

### Pipeline de Treinamento
Execute o script de treinamento:
```bash
python ../../train/train_gamification_cluster.py
```
Verifique se o modelo foi salvo em `models/`.

### Teste de Endpoint
Utilize o teste automatizado:
```bash
pytest ../../tests/test_gamification_service.py
```
Ou manualmente via curl:
```bash
curl -X POST http://localhost:8030/api/gamification-score -H "Content-Type: application/json" -d '{"user_id": "user1", "activity_score": 80, "engagement": 0.7}'
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

Este serviço utiliza modelos de machine learning para segmentação (clustering) e scoring de usuários em gamificação.

## Endpoints
- `/api/gamification-score`: Recebe dados do usuário e retorna cluster e score calculado.

## Treinamento do Modelo
- Utilize o script `train/train_gamification_cluster.py` para treinar e salvar o modelo de clustering.
- Exemplo de uso:
  ```python
  train_and_save_gamification_cluster("../data/gamification_training_data.csv", "../models/gamification_cluster.joblib")
  ```

## Modelos
- Modelos treinados ficam em `models/` (ex: `gamification_cluster.joblib`).

## Exemplo de Dados para Treino
- Estrutura esperada do CSV:
  ```csv
  activity_score,engagement
  80,0.7
  60,0.5
  95,0.9
  ```

## Integração
- O endpoint carrega o modelo real salvo em `models/` e realiza predição baseada nos dados enviados.
