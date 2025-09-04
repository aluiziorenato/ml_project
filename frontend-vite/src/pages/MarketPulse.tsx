// Página MarketPulse

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

const MarketPulse: React.FC = () => {
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
						bgcolor: "#e3fcec",
						border: "2px solid #b2f5ea",
					}}
				>
					<CardHeader
						title={
							<Tooltip
								title="Acompanhe o pulso do mercado em tempo real"
								arrow
							>
								<Typography
									variant="h5"
									fontWeight={700}
									color="success.main"
								>
									Market Pulse
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
							Página de Market Pulse. Adicione aqui os componentes e
							funcionalidades relacionados à análise de mercado.
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

export default MarketPulse;
