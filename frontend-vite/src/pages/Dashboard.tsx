// Dashboard principal da pasta pages

import { Box, Grid, Typography } from "@mui/material";
import React from "react";
import CardDashboard from "./Dashboard/CardDashboard";
import DashboardChart from "./Dashboard/DashboardChart";
import DashboardModal from "./Dashboard/DashboardModal";
import DashboardTable from "./Dashboard/DashboardTable";
import type { DashboardChartData, DashboardMetric } from "./Dashboard/types";

const metrics: DashboardMetric[] = [
	{ id: 1, label: "Vendas", value: 1200, unit: "R$" },
	{ id: 2, label: "Conversões", value: 300, unit: "" },
	{ id: 3, label: "Visitantes", value: 5000, unit: "" },
];

const chartData: DashboardChartData[] = [
	{ label: "Jan", value: 400 },
	{ label: "Fev", value: 800 },
	{ label: "Mar", value: 600 },
];

const Dashboard: React.FC = () => {
	const [modalOpen, setModalOpen] = React.useState(false);
	const [selectedMetric, setSelectedMetric] =
		React.useState<DashboardMetric | null>(null);

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
