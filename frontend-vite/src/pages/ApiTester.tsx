// Página ApiTester

import { Box, Typography } from "@mui/material";
import type React from "react";

const ApiTester: React.FC = () => (
	<Box p={3}>
		<Typography variant="h4" gutterBottom>
			Testador de API
		</Typography>
		<Typography>
			Página para testar APIs. Adicione aqui os componentes e funcionalidades
			para testes de endpoints.
		</Typography>
	</Box>
);

export default ApiTester;
