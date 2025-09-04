import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import { Box, Button, Grid, Typography } from "@mui/material";
import type React from "react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import EditProductModal from "./Products/EditProductModal";
import FiltrosInteligentes from "./Products/FiltrosInteligentes";
import ProductDetailModal from "./Products/ProductDetailModal";
import ProductTable from "./Products/ProductTable";
import type { Produto } from "./Products/types";

const mockProdutos: Produto[] = [
	{
		id: "1",
		nome: "Produto A",
		categoria: "Eletrônicos",
		status: "Ativo",
		preco: 100,
		roi: 12.5,
		sazonalidade: "Alta",
		views: 1500,
		vendas: 300,
		estoque: 50,
		turnover: 2.1,
		imagem: null,
	},
	{
		id: "2",
		nome: "Produto B",
		categoria: "Moda",
		status: "Pendente",
		preco: 200,
		roi: 8.2,
		sazonalidade: "Baixa",
		views: 800,
		vendas: 120,
		estoque: 20,
		turnover: 1.5,
		imagem: null,
	},
];

const Produtos: React.FC = () => {
	const [produtos, setProdutos] = useState<Produto[]>(mockProdutos);
	const [modalEditOpen, setModalEditOpen] = useState(false);
	const [modalDetailOpen, setModalDetailOpen] = useState(false);
	const [produtoSelecionado, setProdutoSelecionado] = useState<Produto | null>(
		null,
	);

	const navigate = useNavigate();
	const handleAdd = () => {
		navigate("/novo-anuncio");
	};
	const handleEdit = (produto: Produto) => {
		setProdutoSelecionado(produto);
		setModalEditOpen(true);
	};
	const handleDetail = (produto: Produto) => {
		setProdutoSelecionado(produto);
		setModalDetailOpen(true);
	};
	const handleSave = (updated: Produto) => {
		if (updated.id) {
			setProdutos(produtos.map((p) => (p.id === updated.id ? updated : p)));
		} else {
			setProdutos([
				...produtos,
				{ ...updated, id: String(produtos.length + 1) },
			]);
		}
		setModalEditOpen(false);
	};

	return (
		<Box
			sx={{
				p: 4,
				background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
				minHeight: "100vh",
			}}
		>
			<Grid container alignItems="center" justifyContent="space-between" mb={3}>
				<Grid item>
					<Typography
						variant="h3"
						fontWeight={700}
						color="#2d3a4a"
						gutterBottom
					>
						Produtos
					</Typography>
				</Grid>
				<Grid item>
					<Button
						variant="contained"
						startIcon={<AddCircleOutlineIcon />}
						onClick={handleAdd}
						sx={{
							background: "linear-gradient(90deg, #ffb300 0%, #ff6f00 100%)",
							color: "#fff",
							fontWeight: 600,
							boxShadow: 2,
							borderRadius: 2,
							px: 3,
							py: 1.5,
							"&:hover": {
								background: "linear-gradient(90deg, #ff6f00 0%, #ffb300 100%)",
							},
						}}
					>
						Novo Produto
					</Button>
				</Grid>
			</Grid>
			<Box mb={3}>
				<FiltrosInteligentes onChange={() => {}} />
			</Box>
			<Box sx={{ boxShadow: 3, borderRadius: 3, background: "#fff", p: 3 }}>
				<ProductTable produtos={produtos} onSelect={handleDetail} />
			</Box>
			<EditProductModal
				open={modalEditOpen}
				produto={produtoSelecionado}
				onClose={() => setModalEditOpen(false)}
				onSave={handleSave}
			/>
			<ProductDetailModal
				open={modalDetailOpen}
				produto={produtoSelecionado}
				onClose={() => setModalDetailOpen(false)}
			/>
		</Box>
	);
};

export default Produtos;
