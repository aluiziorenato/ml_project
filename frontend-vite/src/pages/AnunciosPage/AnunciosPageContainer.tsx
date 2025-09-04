// Container principal da página de Anúncios
// Importa o componente original para dentro da nova estrutura modular

import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import { Box, Button } from "@mui/material";
import type React from "react";
import AnunciosTable from "./AnunciosTable";
import type { Anuncio } from "./types";

const mockAnuncios: Anuncio[] = [
	{
		id: 1,
		imagem:
			"https://http2.mlstatic.com/D_NQ_NP_2X_954825-MLB54981385767_042023-F.webp",
		titulo: "Smartphone Samsung Galaxy S23 Ultra 256GB",
		preco: 5999.99,
		categoria: "Eletrônicos",
		tipo: "gold_pro",
		frete: 29.9,
		desconto: 10,
		promocao: true,
		estoque: 15,
		variacoes: [],
		vendas: 120,
		visitas: 350,
		relevancia: 87,
	},
	{
		id: 2,
		imagem:
			"https://http2.mlstatic.com/D_NQ_NP_2X_954825-MLB54981385767_042023-F.webp",
		titulo: "Notebook Dell Inspiron 15 8GB 256GB SSD",
		preco: 3999.9,
		categoria: "Informática",
		tipo: "gold_special",
		frete: 19.9,
		desconto: 5,
		promocao: false,
		estoque: 8,
		variacoes: [],
		vendas: 45,
		visitas: 80,
		relevancia: 65,
	},
];

const AnunciosPageContainer: React.FC = () => (
	<Box p={2}>
		<Button variant="contained" startIcon={<AddCircleOutlineIcon />}>
			Novo Anúncio
		</Button>
		<AnunciosTable anuncios={mockAnuncios} />
	</Box>
);

export default AnunciosPageContainer;
