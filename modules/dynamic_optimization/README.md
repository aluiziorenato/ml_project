# Dynamic Optimization

## Endpoints
- `/api/optimize-title`: Otimização de títulos usando modelo ML real.
- `/api/optimize-price`: Sugestão de preços baseada em modelo de regressão.
- `/api/optimize-timing`: Otimização de timing baseada em dados históricos.
- `/api/ab-test`: Testes A/B automáticos.
- `/api/analytics/dashboard`: Dashboard de métricas.

## Treinamento de Modelos
- Scripts em `train/` para treinamento dos modelos de título e preço.
- Dados de exemplo em `data/`.
- Modelos salvos em `models/` com versionamento por timestamp.

## Monitoramento e Explicabilidade
- `app/monitor.py`: Monitoramento de métricas dos modelos.
- `app/explain.py`: Explicabilidade das previsões via SHAP.

## Testes Automatizados
- Testes unitários e de integração em `tests/` para endpoints e modelos ML.

## Integração
- Conexão com banco PostgreSQL via porta padrão 5432 e variáveis de ambiente.
- Persistência dos dados e modelos conforme padrão do projeto.

## Re-treinamento
- Execute scripts de treinamento sempre que houver novos dados ou mudanças de mercado.

## Como usar
1. Treine os modelos com os scripts em `train/`.
2. Inicie o serviço e acesse os endpoints para otimização.
3. Monitore métricas e explicabilidade.
4. Execute testes automatizados para garantir funcionamento.

---

> Para novos serviços ML, siga o mesmo padrão de organização, integração e documentação.
