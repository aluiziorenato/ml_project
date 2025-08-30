
const express = require('express');
const app = express();
const PORT = 3003;

// Gera dados robustos para produtos e tendências
function gerarProdutosECategorias() {
  const categorias = [
    'Eletrônicos', 'Moda', 'Casa', 'Esportes', 'Beleza', 'Brinquedos', 'Livros', 'Automotivo', 'Pet', 'Mercado',
    'Informática', 'Móveis', 'Ferramentas', 'Saúde', 'Cozinha', 'Jardim', 'Games', 'Música', 'Bebidas', 'Infantil'
  ];
  const produtosPorCategoria = {};
  let id = 1;
  categorias.forEach(cat => {
    produtosPorCategoria[cat] = [];
    for (let i = 0; i < 8 + Math.floor(Math.random() * 8); i++) {
      produtosPorCategoria[cat].push({
        id: id++,
        titulo: `${cat} Produto ${i + 1}`,
        preco: Number((Math.random() * 5000 + 20).toFixed(2)),
        vendas: Math.floor(Math.random() * 800 + 10),
        imagem: `https://placehold.co/80x80?text=${cat}+${i + 1}`
      });
    }
  });
  return produtosPorCategoria;
}

function gerarTendencias(produtosPorCategoria, dias = 30) {
  const tendenciasPorCategoria = {};
  Object.keys(produtosPorCategoria).forEach(cat => {
    const arr = [];
    for (let d = 0; d < dias; d++) {
      arr.push({
        ds: `2025-08-${String(d + 1).padStart(2, '0')}`,
        y: produtosPorCategoria[cat].reduce((acc, prod) => acc + Math.floor(Math.random() * 30 + 10), 0)
      });
    }
    tendenciasPorCategoria[cat] = arr;
  });
  return tendenciasPorCategoria;
}

const produtosPorCategoria = gerarProdutosECategorias();
const tendenciasPorCategoria = gerarTendencias(produtosPorCategoria, 30);

// Endpoint único para produtos por categoria
app.get('/api/produtos', (req, res) => {
  const categoria = req.query.categoria;
  if (categoria && produtosPorCategoria[categoria]) {
    res.json({ [categoria]: produtosPorCategoria[categoria] });
  } else {
    res.json(produtosPorCategoria);
  }
});

// Endpoint único para tendências por categoria
app.get('/api/tendencias', (req, res) => {
  const categoria = req.query.categoria;
  if (categoria && tendenciasPorCategoria[categoria]) {
    res.json({ [categoria]: tendenciasPorCategoria[categoria] });
  } else {
    res.json(tendenciasPorCategoria);
  }
});

app.listen(PORT, () => {
  console.log(`Mock API rodando em http://localhost:${PORT}`);
});
