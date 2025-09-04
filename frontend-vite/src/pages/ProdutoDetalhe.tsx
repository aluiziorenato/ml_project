// Página ProdutoDetalhe

import { Box, Typography } from "@mui/material";
import type React from "react";

const ProdutoDetalhe: React.FC = () => (
	<Box p={3}>
		<Typography variant="h4" gutterBottom>
			Produto Detalhe
		</Typography>
		<Typography>
			Página de detalhes do produto. Adicione aqui os componentes e
			funcionalidades relacionados ao produto.
		</Typography>
	</Box>
);

export default ProdutoDetalhe;
