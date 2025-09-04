// Página OAuthManager

import { Box, Typography } from "@mui/material";
import type React from "react";

const OAuthManager: React.FC = () => (
	<Box p={3}>
		<Typography variant="h4" gutterBottom>
			Gerenciador de OAuth
		</Typography>
		<Typography>
			Página para gerenciamento de OAuth. Adicione aqui os componentes e
			funcionalidades relacionados à autenticação OAuth.
		</Typography>
	</Box>
);

export default OAuthManager;
