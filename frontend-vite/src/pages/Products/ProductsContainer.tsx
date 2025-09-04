// Container principal da página de Produtos
// Importa o componente original para dentro da nova estrutura modular

import { Box, Typography } from "@mui/material";
import type React from "react";

const ProductsContainer: React.FC = () => (
	<Box p={2}>
		<Typography variant="h6">Container de Produtos</Typography>
		{/* Adicione aqui lógica, cards, filtros, etc. do container */}
	</Box>
);

export default ProductsContainer;
