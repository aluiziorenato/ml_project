# Cross Platform

## Endpoints
- `/api/platform-performance`: Métricas reais de desempenho multi-plataforma usando modelos ML.
- `/health`: Health check do serviço.

## Treinamento de Modelos
- Script em `train/train_platform_model.py` para treinamento dos modelos de previsão de desempenho.
- Dados de exemplo em `data/platform_training_data.csv`.
- Modelos salvos em `models/` com versionamento por timestamp.

## Monitoramento e Explicabilidade
- `app/monitor.py`: Métricas dos modelos (acurácia, uso, drift).
- `app/explain.py`: Explicabilidade das previsões via SHAP.

## Testes Automatizados
- Testes unitários e de integração em `tests/` para endpoints e modelos ML.

## Integração
- Conexão com banco PostgreSQL via porta padrão 5432 e variáveis de ambiente.
- Persistência dos dados e modelos conforme padrão do projeto.

## Re-treinamento
- Execute o script de treinamento sempre que houver novos dados ou mudanças de mercado.

## Como usar
1. Treine os modelos com o script em `train/`.
2. Inicie o serviço e acesse o endpoint para métricas multi-plataforma.
3. Monitore métricas e explicabilidade.
4. Execute testes automatizados para garantir funcionamento.

---

> Para novos serviços ML, siga o mesmo padrão de organização, integração e documentação.
