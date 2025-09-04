import {
	Button,
	CircularProgress,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
} from "@mui/material";
				style={{
					marginBottom: 16,
					fontSize: 20,
					fontWeight: 600,
					color: "#11110D",
					letterSpacing: 0.2,
				}}
			>
				Produtos
			</h2>
			{/* Gráfico de barras premium - Quantidade de produtos por categoria */}
			<div
				style={{
					width: "100%",
					maxWidth: 600,
					margin: "0 auto 32px auto",
					background: "#fff",
					borderRadius: 12,
					boxShadow: "0 2px 12px #e5e7eb",
					padding: 24,
				}}
			>
				<h3
					style={{
						fontSize: 16,
						fontWeight: 500,
						color: "#1976D2",
						marginBottom: 12,
						letterSpacing: 0.2,
					}}
				>
					Distribuição de Produtos por Categoria
				</h3>
				<ResponsiveContainer width="100%" height={260}>
					<BarChart
						data={dadosGrafico}
						margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
					>
						<CartesianGrid strokeDasharray="3 3" />
						<XAxis
							dataKey="categoria"
							fontSize={13}
							tick={{ fill: "#11110D" }}
						/>
						<YAxis
							fontSize={13}
							tick={{ fill: "#11110D" }}
							allowDecimals={false}
						/>
						<Tooltip
							wrapperStyle={{ fontSize: 13 }}
							contentStyle={{ borderRadius: 8 }}
						/>
						<Legend wrapperStyle={{ fontSize: 13 }} />
						<Bar
							dataKey="quantidade"
							fill="#1976D2"
							radius={[8, 8, 0, 0]}
							barSize={38}
							name="Produtos"
						/>
					</BarChart>
				</ResponsiveContainer>
			</div>
			<button
				style={{
					marginBottom: 16,
					fontSize: 15,
					padding: "8px 22px",
					borderRadius: 6,
					background: "#1976D2",
					color: "#fff",
					border: "none",
					boxShadow: "0 2px 8px #e5e7eb",
					cursor: "pointer",
					transition: "background 0.2s, box-shadow 0.2s",
				}}
				onMouseOver={(e) => (e.currentTarget.style.background = "#1565c0")}
				onMouseOut={(e) => (e.currentTarget.style.background = "#1976D2")}
				onClick={() => handleOpenForm()}
			>
				Cadastrar Produto
			</button>
			<div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
				<input
					type="text"
					placeholder="Filtrar por título"
					value={filtroTitulo}
					onChange={(e) => setFiltroTitulo(e.target.value)}
					style={{
						padding: 8,
						borderRadius: 6,
						border: "1px solid #E5E7EB",
						minWidth: 180,
						fontSize: 13,
						background: "#fff",
						transition: "border 0.2s",
					}}
				/>
				<select
					value={filtroCategoria}
					onChange={(e) => setFiltroCategoria(e.target.value)}
					style={{
						padding: 8,
						borderRadius: 6,
						border: "1px solid #E5E7EB",
						fontSize: 13,
						background: "#fff",
						transition: "border 0.2s",
					}}
				>
					<option value="">Todas categorias</option>
					{[...new Set(produtos.map((p) => p.categoria))].map((cat) => (
						<option key={cat} value={cat}>
							{cat}
						</option>
					))}
				</select>
				<select
					value={filtroStatus}
					onChange={(e) => setFiltroStatus(e.target.value)}
					style={{
						padding: 8,
						borderRadius: 6,
						border: "1px solid #E5E7EB",
						fontSize: 13,
						background: "#fff",
						transition: "border 0.2s",
					}}
				>
					<option value="">Todos status</option>
					{[...new Set(produtos.map((p) => p.status))].map((st) => (
						<option key={st} value={st}>
							{st}
						</option>
					))}
				</select>
				<select
					value={ordemPreco}
					onChange={(e) => setOrdemPreco(e.target.value)}
					style={{
						padding: 8,
						borderRadius: 6,
						border: "1px solid #E5E7EB",
						fontSize: 13,
						background: "#fff",
						transition: "border 0.2s",
					}}
				>
					<option value="desc">Maior preço</option>
					<option value="asc">Menor preço</option>
				</select>
			</div>
			<div style={{ width: "100%", maxWidth: 1100, margin: "0 auto" }}>
				{produtosFiltrados.length === 0 ? (
					<div style={{ marginTop: 32, textAlign: "center" }}>
						Nenhum produto encontrado.
					</div>
				) : (
					<table
						style={{
							width: "100%",
							borderCollapse: "separate",
							borderSpacing: 0,
							marginTop: 16,
							background: "#fff",
							boxShadow: "0 2px 8px #e5e7eb",
							fontSize: 13,
							borderRadius: 8,
							overflow: "hidden",
						}}
					>
						<thead style={{ background: "#F6F7F9" }}>
							<tr>
								<th
									style={{
										padding: 10,
										fontWeight: 600,
										fontSize: 13,
										color: "#11110D",
										borderBottom: "1px solid #E5E7EB",
									}}
								>
									Imagem
								</th>
								<th
									style={{
										padding: 10,
										fontWeight: 600,
										fontSize: 13,
										color: "#11110D",
										borderBottom: "1px solid #E5E7EB",
									}}
								>
									Título
								</th>
								<th
									style={{
										padding: 10,
										fontWeight: 600,
										fontSize: 13,
										color: "#11110D",
										borderBottom: "1px solid #E5E7EB",
									}}
								>
									Preço
								</th>
								<th
									style={{
										padding: 10,
										fontWeight: 600,
										fontSize: 13,
										color: "#11110D",
										borderBottom: "1px solid #E5E7EB",
									}}
								>
									Status
								</th>
								<th
									style={{
										padding: 10,
										fontWeight: 600,
										fontSize: 13,
										color: "#11110D",
										borderBottom: "1px solid #E5E7EB",
									}}
								>
									Estoque
								</th>
								<th
									style={{
										padding: 10,
										fontWeight: 600,
										fontSize: 13,
										color: "#11110D",
										borderBottom: "1px solid #E5E7EB",
									}}
								>
									Categoria
								</th>
								<th
									style={{
										padding: 10,
										fontWeight: 600,
										fontSize: 13,
										color: "#11110D",
										borderBottom: "1px solid #E5E7EB",
									}}
								>
									Ações
								</th>
							</tr>
						</thead>
						<tbody>
							{produtosFiltrados.map((produto, idx) => (
								<tr
									key={produto.id}
									style={{
										borderBottom: "1px solid #E5E7EB",
										fontSize: 13,
										background: idx % 2 === 0 ? "#fff" : "#F6F7F9",
										transition: "background 0.2s",
									}}
									onMouseOver={(e) =>
										(e.currentTarget.style.background = "#E5E7EB")
									}
									onMouseOut={(e) =>
										(e.currentTarget.style.background =
											idx % 2 === 0 ? "#fff" : "#F6F7F9")
									}
								>
									<td style={{ padding: 10, textAlign: "center" }}>
										<img
											src={
												produto.imagem ||
												"https://via.placeholder.com/80x80.png?text=Produto"
											}
											alt={produto.nome}
											style={{
												width: 56,
												height: 56,
												objectFit: "cover",
												borderRadius: 8,
												border: "1px solid #E5E7EB",
												boxShadow: "0 1px 4px #e5e7eb",
											}}
										/>
									</td>
									<td style={{ padding: 10 }}>{produto.nome}</td>
									<td
										style={{ padding: 10, fontWeight: 600, color: "#1976D2" }}
									>
										R$ {produto.preco}
									</td>
									<td style={{ padding: 10 }}>{produto.status}</td>
									<td style={{ padding: 10 }}>{produto.estoque}</td>
									<td style={{ padding: 10 }}>{produto.categoria}</td>
									<td style={{ padding: 10 }}>
										<button
											style={{
												marginRight: 8,
												fontSize: 15,
												padding: "7px 18px",
												borderRadius: 6,
												background: "#10B981",
												color: "#fff",
												border: "none",
												boxShadow: "0 2px 8px #e5e7eb",
												cursor: "pointer",
												transition: "background 0.2s, box-shadow 0.2s",
											}}
											onMouseOver={(e) =>
												(e.currentTarget.style.background = "#059669")
											}
											onMouseOut={(e) =>
												(e.currentTarget.style.background = "#10B981")
											}
											onClick={() => handleOpenForm(produto)}
										>
											Editar
										</button>
										<button
											style={{
												marginRight: 8,
												fontSize: 15,
												padding: "7px 18px",
												borderRadius: 6,
												background: "#F43F5E",
												color: "#fff",
												border: "none",
												boxShadow: "0 2px 8px #e5e7eb",
												cursor: "pointer",
												transition: "background 0.2s, box-shadow 0.2s",
											}}
											onMouseOver={(e) =>
												(e.currentTarget.style.background = "#be123c")
											}
											onMouseOut={(e) =>
												(e.currentTarget.style.background = "#F43F5E")
											}
											onClick={() => setConfirmDelete(produto)}
										>
											Excluir
										</button>
									</td>
								</tr>
							))}
						</tbody>
					</table>
				)}
			</div>
			{/* Modal de cadastro/edição */}
			<Dialog open={openForm} onClose={handleCloseForm} maxWidth="md" fullWidth>
				<DialogTitle style={{ fontSize: 16 }}>
					{produtoEdit ? "Alterar Produto" : "Cadastrar Produto"}
				</DialogTitle>
				<DialogContent style={{ fontSize: 13 }}>
					<ProdutoForm
						produto={produtoEdit || {}}
						onSubmit={handleSubmit}
						onCancel={handleCloseForm}
					/>
				</DialogContent>
			</Dialog>
			{/* Modal de confirmação de exclusão */}
			<Dialog open={!!confirmDelete} onClose={() => setConfirmDelete(null)}>
				<DialogTitle style={{ fontSize: 16 }}>Excluir Produto</DialogTitle>
				<DialogContent style={{ fontSize: 13 }}>
					Tem certeza que deseja excluir o produto "
					{confirmDelete?.nome || confirmDelete?.titulo}"?
				</DialogContent>
				<DialogActions>
					<Button
						onClick={() => setConfirmDelete(null)}
						color="secondary"
						style={{ fontSize: 13 }}
					>
						Cancelar
					</Button>
					<Button
						onClick={() => handleDelete(confirmDelete.id)}
						color="error"
						style={{ fontSize: 13 }}
					>
						Excluir
					</Button>
				</DialogActions>
			</Dialog>
		</div>
	);
}
export default Produtos;
