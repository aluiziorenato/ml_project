// Página Products

import { Box, Typography, Button } from "@mui/material";
import type React from "react";
import FiltrosInteligentes from "./Products/FiltrosInteligentes";
import ProductsContainer from "./Products/ProductsContainer";
import ProductTable from "./Products/ProductTable";

const Products: React.FC = () => (
	<Box p={3}>
		<Typography variant="h4" gutterBottom>
			Produtos (Products)
		</Typography>
	<Box sx={{ display: "flex", justifyContent: "flex-end", mb: 2 }}>
		{/* Navegação SPA para Novo Anúncio */}
		<Button
			component={require("react-router-dom").Link}
			to="/novo-anuncio"
			variant="contained"
			color="primary"
			sx={{ fontWeight: 700 }}
		>
			NOVO PRODUTO
		</Button>
	</Box>
		<FiltrosInteligentes />
		<ProductsContainer />
		<ProductTable />
	</Box>
);

export default Products;
