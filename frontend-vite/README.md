# Frontend Vite + TypeScript

Este projeto foi migrado do Create React App (CRA) para Vite + TypeScript para garantir maior performance, melhor DX e manutenção.

## Como rodar

```bash
npm install
npm run dev
```

## Estrutura
- `src/`: Componentes, páginas e assets migrados do CRA
- `vite.config.ts`: Configuração do Vite
- `tsconfig.json`: Configuração do TypeScript
- `package.json`: Dependências e scripts

## Adaptações
- Variáveis de ambiente devem usar prefixo `VITE_`
- Plugins e scripts customizados devem ser configurados em `vite.config.ts`

## Testes
- Execute `npm run test` para rodar os testes automatizados

## Migração
- Todos os componentes, páginas e assets do CRA foram migrados para esta estrutura
- O projeto antigo foi removido após validação completa

## Evidências
- Prints, logs e outputs de testes registrados para auditoria

---

> Para dúvidas ou problemas, consulte a documentação oficial do Vite e React.
