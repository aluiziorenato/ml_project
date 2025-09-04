// Página Concorrentes

import { Box, Typography } from "@mui/material";
import type React from "react";

import CompetitorTable from "./CompetitorIntelligence/CompetitorTable";
import PriceHistoryTable from "./CompetitorIntelligence/PriceHistoryTable";

const Concorrentes: React.FC = () => (
	<Box p={3}>
		<Typography variant="h4" gutterBottom>
			Concorrentes
		</Typography>
		<CompetitorTable
			concorrentes={[
				{ id: "1", nome: "Empresa A", segmento: "Varejo", preco: 100 },
				{ id: "2", nome: "Empresa B", segmento: "Serviços", preco: 200 },
			]}
			onSelect={() => {}}
		/>
		<PriceHistoryTable
			historico={[
				{ id: "1", produto: "Produto X", preco: 100, data: "2025-08-30" },
				{ id: "2", produto: "Produto Y", preco: 200, data: "2025-08-29" },
			]}
		/>
	</Box>
);

export default Concorrentes;
