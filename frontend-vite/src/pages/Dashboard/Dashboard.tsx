// Página principal do Dashboard

import { Box, Grid, Typography } from "@mui/material";
import type React from "react";
import { useState } from "react";
import CardDashboard from "./CardDashboard";
import DashboardChart from "./DashboardChart";
import DashboardModal from "./DashboardModal";
import DashboardTable from "./DashboardTable";
import type { DashboardChartData, DashboardMetric } from "./types";

// Exemplo de dados mockados
const metrics: DashboardMetric[] = [
	{ id: 1, label: "Vendas", value: 1200, unit: "R$" },
	{ id: 2, label: "Conversões", value: 300, unit: "" },
	{ id: 3, label: "Visitantes", value: 5000, unit: "" },
];

const chartData: DashboardChartData[] = [
	{ name: "Jan", value: 400 },
	{ name: "Fev", value: 800 },
	{ name: "Mar", value: 600 },
];

const Dashboard: React.FC = () => {
	const [modalOpen, setModalOpen] = useState(false);
	const [selectedMetric, setSelectedMetric] = useState<DashboardMetric | null>(
		null,
	);

	const handleCardClick = (metric: DashboardMetric) => {
		setSelectedMetric(metric);
		setModalOpen(true);
	};

	const handleCloseModal = () => {
		setModalOpen(false);
		setSelectedMetric(null);
	};

	return (
		<Box p={3}>
			<Typography variant="h4" gutterBottom>
				Dashboard
			</Typography>
			<Grid container spacing={2}>
				{metrics.map((metric) => (
					<Grid item xs={12} sm={4} key={metric.id}>
						<div
							onClick={() => handleCardClick(metric)}
							style={{ cursor: "pointer" }}
						>
							<CardDashboard metric={metric} />
						</div>
					</Grid>
				))}
			</Grid>
			<Box mt={4}>
				<DashboardChart data={chartData} title="Vendas por mês" />
			</Box>
			<Box mt={4}>
				<DashboardTable metrics={metrics} />
			</Box>
			{selectedMetric && (
				<DashboardModal
					open={modalOpen}
					metricLabel={selectedMetric.label}
					metricValue={selectedMetric.value}
					onClose={handleCloseModal}
				/>
			)}
		</Box>
	);
};

export default Dashboard;
