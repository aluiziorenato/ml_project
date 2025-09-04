// Página MetricasPage

import { Box, Typography } from "@mui/material";
import React, { useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Divider from "@mui/material/Divider";
import Tooltip from "@mui/material/Tooltip";
import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import Button from "@mui/material/Button";
import { motion } from "framer-motion";

const MetricasPage: React.FC = () => {
	const [snackbar, setSnackbar] = useState({
		open: false,
		message: "",
		severity: "success",
	});
	return (
		<Box sx={{ bgcolor: "#f7fafc", minHeight: "100vh", py: 4 }}>
			<Box
				sx={{
					maxWidth: 700,
					mx: "auto",
					px: { xs: 1, sm: 2, md: 0 },
				}}
			>
				<Card
					elevation={4}
					sx={{
						mb: 4,
						bgcolor: "#fffbe6",
						border: "2px solid #ffe066",
					}}
				>
					<CardHeader
						title={
							<Tooltip
								title="Veja as métricas detalhadas do sistema"
								arrow
							>
								<Typography
									variant="h5"
									fontWeight={700}
									color="warning.main"
								>
									Métricas
								</Typography>
							</Tooltip>
						}
					/>
					<Divider />
					<CardContent>
						<Typography
							variant="body1"
							color="text.secondary"
							gutterBottom
						>
							Página de métricas. Adicione aqui os componentes e
							funcionalidades relacionadas às métricas do sistema.
						</Typography>
						<motion.div
							whileHover={{ scale: 1.04 }}
							whileTap={{ scale: 0.98 }}
						>
							<Button
								variant="contained"
								color="primary"
								sx={{ mt: 2, fontWeight: 700 }}
								onClick={() =>
									setSnackbar({
										open: true,
										message: "Ação de exemplo executada!",
										severity: "success",
									})
								}
							>
								Ação de exemplo
							</Button>
						</motion.div>
					</CardContent>
				</Card>
				<Snackbar
					open={snackbar.open}
					autoHideDuration={3000}
					onClose={() =>
						setSnackbar({ ...snackbar, open: false })
					}
					anchorOrigin={{
						vertical: "top",
						horizontal: "center",
					}}
				>
					<Alert
						severity={
							snackbar.severity as
								| "success"
								| "error"
								| "info"
								| "warning"
						}
						sx={{ width: "100%" }}
					>
						{snackbar.message}
					</Alert>
				</Snackbar>
			</Box>
		</Box>
	);
};

export default MetricasPage;
