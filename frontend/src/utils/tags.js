// src/utils/tags.js
export function computeTags(prod, cfg = {}) {
  const {
    minViews = 1000,
    minConv = 0.02,
    minTurnover = 5,
    maxEstoque = 50,
  } = cfg;

  const views = Number(prod?.views ?? 0);
  const vendas = Number(prod?.vendas ?? 0);
  const estoque = Number(prod?.estoque ?? 0);
  const turnover = Number(prod?.turnover ?? 0);

  const conversao = views > 0 ? vendas / views : 0;

  return {
    altaDemanda: views >= minViews && conversao >= minConv,
    baixaConcorrencia: turnover >= minTurnover && estoque <= maxEstoque,
    metrics: { views, vendas, conversao, estoque, turnover },
  };
}
