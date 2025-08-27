# ROI Prediction

## Endpoints
- `/api/predict-roi`: Predição de ROI usando modelo HistGradientBoostingRegressor real.
- `/health`: Health check do serviço.
- `/api/status`: Status do modelo.

## Treinamento de Modelo
- Script em `train/train_roi_model.py` para treinamento do modelo HistGradientBoostingRegressor.
- Dados de exemplo em `data/roi_training_data.csv`.
- Modelos salvos em `models/` com versionamento por timestamp.

## Mapeamento de Campos de Entrada
- investimento
- cliques
- conversoes
- impressoes

## Monitoramento e Explicabilidade
- `app/monitor.py`: Métricas do modelo (acurácia, uso, drift).
- `app/explain.py`: Explicabilidade das previsões via SHAP.

## Testes Automatizados
- Testes unitários e de integração em `tests/` para endpoints e modelo ML.

## Integração
- Conexão com banco PostgreSQL via porta padrão 5432 e variáveis de ambiente.
- Persistência dos dados e modelos conforme padrão do projeto.

## Re-treinamento
- Execute o script de treinamento sempre que houver novos dados ou mudanças de mercado.

## Como usar
1. Treine o modelo com o script em `train/`.
2. Inicie o serviço e acesse o endpoint para predição de ROI.
3. Monitore métricas e explicabilidade.
4. Execute testes automatizados para garantir funcionamento.

---

> Para novos serviços ML, siga o mesmo padrão de organização, integração e documentação.
