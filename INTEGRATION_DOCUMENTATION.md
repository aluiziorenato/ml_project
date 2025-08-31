# Documentação de Integração entre learning_service e strategic_mode_service

## Canais Redis Utilizados
- `learning_events`: eventos publicados pelo learning_service (anomalias, recomendações, alertas)
- `user_strategy_events`: escolhas de estratégia feitas pelo usuário via menu dinâmico

## Formatos de Payload
```json
{
  "type": "anomaly|recommendation|alert|user_strategy_selection",
  "timestamp": "2025-08-30T12:00:00Z",
  "details": { ... }
}
```

## Exemplos de Eventos
- Anomalia:
```json
{
  "type": "anomaly",
  "timestamp": "2025-08-30T12:00:00Z",
  "details": {"score": 0.98, "feature": "latency"}
}
```
- Recomendação:
```json
{
  "type": "recommendation",
  "timestamp": "2025-08-30T12:00:00Z",
  "details": {"action": "increase_bid", "product_id": 12345}
}
```
- Seleção de estratégia pelo usuário:
```json
{
  "type": "user_strategy_selection",
  "timestamp": "2025-08-30T12:00:00Z",
  "details": {"strategy": "competitivo", "parameters": {"budget": 1000}}
}
```

## Fluxos
- learning_service publica eventos em `learning_events`.
- strategic_mode_service consome eventos e ativa modos estratégicos.
- Usuário seleciona estratégia via menu, que publica em `user_strategy_events`.
- strategic_mode_service consome e aplica a escolha do usuário.

## Troubleshooting
- Verifique logs: `learning_service_integration.log`, `strategic_mode_service_integration.log`, `strategic_mode_service_user_strategy.log`.
- Certifique-se que Redis está ativo e acessível.
- Teste publicação e consumo com scripts de exemplo.

## Checklist Crítico
- [x] Redis configurado e seguro
- [x] Eventos padronizados
- [x] Logs e auditoria ativos
- [x] Testes automatizados sugeridos
- [x] Documentação clara
