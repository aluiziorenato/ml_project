
---

## 📁 app/services/README.md

```markdown
# 🔧 Services — Lógica de Negócio e Integrações

Contém funções que encapsulam regras de negócio e chamadas a serviços externos.

## 📌 Objetivo

- Separar lógica da camada de API.
- Facilitar testes e reutilização de código.

## 📁 Exemplos

- `mercado_libre.py`: integração com API externa.
- `email_service.py`: envio de notificações.

## 🧠 Boas Práticas

- Mantenha funções puras e testáveis.
- Evite acoplamento com rotas ou modelos diretamente.
- Use `httpx` ou `requests` com timeout e tratamento de erros.

## 🧪 Testes

- Use mocks para simular respostas externas.
- Teste comportamento esperado e falhas.
