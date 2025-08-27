// src/services/productService.js
export async function carregarProdutos() {
  // Simula pequeno delay de rede
  await new Promise((r) => setTimeout(r, 200));

  return [
    {
      id: 1,
      nome: "Fone Bluetooth",
      categoria: "Eletrônicos",
      status: "Ativo",
      preco: 199,
      roi: 2.5,
      sazonalidade: "Média",
      views: 5000,
      vendas: 200,
      estoque: 30,
      turnover: 6,
      imagem: "https://via.placeholder.com/80x80.png?text=Fone"
    },
    {
      id: 2,
      nome: "Liquidificador Turbo",
      categoria: "Casa",
      status: "Ativo",
      preco: 299,
      roi: 1.4,
      sazonalidade: "Baixa",
      views: 400,
      vendas: 10,
      estoque: 120,
      turnover: 2,
      imagem: "https://via.placeholder.com/80x80.png?text=Liquidificador"
    },
    {
      id: 3,
      nome: "Camiseta Dry",
      categoria: "Moda",
      status: "Esgotado",
      preco: 79,
      roi: 3.2,
      sazonalidade: "Alta",
      views: 2000,
      vendas: 120,
      estoque: 10,
      turnover: 8,
      imagem: "https://via.placeholder.com/80x80.png?text=Camiseta"
    },
    {
      id: 4,
      nome: "Notebook Ultra",
      categoria: "Informática",
      status: "Ativo",
      preco: 4500,
      roi: 1.8,
      sazonalidade: "Média",
      views: 12000,
      vendas: 500,
      estoque: 15,
      turnover: 20,
      imagem: "https://via.placeholder.com/80x80.png?text=Notebook"
    },
    {
      id: 5,
      nome: "Smartwatch Fit",
      categoria: "Eletrônicos",
      status: "Ativo",
      preco: 899,
      roi: 2.1,
      sazonalidade: "Baixa",
      views: 3000,
      vendas: 150,
      estoque: 40,
      turnover: 7,
      imagem: "https://via.placeholder.com/80x80.png?text=Smartwatch"
    }
  ];
}
