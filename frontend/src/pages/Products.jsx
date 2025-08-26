// src/pages/Products.jsx
import { useEffect, useMemo, useState } from "react";
import { carregarProdutos } from "../services/productService";
import {
  Box,
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import FiltrosInteligentes from "../components/FiltrosInteligentes";

function useUserId() {
  return "user-123";
}

function computeTags(prod) {
  const views = Number(prod?.views ?? 0);
  const vendas = Number(prod?.vendas ?? 0);
  const estoque = Number(prod?.estoque ?? 0);
  const turnover = Number(prod?.turnover ?? 0);
  const conversao = views > 0 ? vendas / views : 0;
  const altaDemanda = views >= 1000 && conversao >= 0.02;
  const baixaConcorrencia = turnover >= 5 && estoque <= 50;
  return { altaDemanda, baixaConcorrencia };
}

function getLSKey(userId) {
  return `filters:${userId ?? "anon"}`;
}

export default function Products() {
  const userId = useUserId();
  const [loading, setLoading] = useState(false);
  const [allProducts, setAllProducts] = useState([]);
  const [activeFilters, setActiveFilters] = useState(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      try {
        const raw = await carregarProdutos();
        const data = (Array.isArray(raw) ? raw : []).map((p) => ({
          id: p.id,
          nome: p.nome ?? "-",
          categoria: p.categoria ?? "-",
          status: p.status ?? "Ativo",
          preco: Number(p.preco ?? 0),
          roi: Number(p.roi ?? 0),
          sazonalidade: p.sazonalidade ?? "",
          views: Number(p.views ?? 0),
          vendas: Number(p.vendas ?? 0),
          estoque: Number(p.estoque ?? 0),
          turnover: Number(p.turnover ?? 0),
          imagem: p.imagem ?? null,
        }));
        if (mounted) setAllProducts(data);
      } catch (err) {
        console.error("Erro ao carregar produtos:", err);
        if (mounted) setAllProducts([]);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const initialFilters = useMemo(() => {
    try {
      const raw = localStorage.getItem(getLSKey(userId));
      return raw ? JSON.parse(raw) : undefined;
    } catch {
      return undefined;
    }
  }, [userId]);

  const handleFilter = (f) => setActiveFilters(f);

  const filteredProducts = useMemo(() => {
    if (!activeFilters) return allProducts;
    const { categorias = [], status = [], preco = [0, Infinity], roiMin = 0, sazonalidade = "", tags = {} } = activeFilters;

    return allProducts.filter((p) => {
      const tagsP = computeTags(p);
      const passCategoria = categorias.length ? categorias.includes(p.categoria) : true;
      const passStatus = status.length ? status.includes(p.status) : true;
      const passPreco = p.preco >= preco[0] && p.preco <= (preco[1] ?? Infinity);
      const passROI = p.roi >= roiMin;
      const passSazonalidade = sazonalidade ? p.sazonalidade === sazonalidade : true;
      const passTagAlta = tags?.altaDemanda ? tagsP.altaDemanda : true;
      const passTagBaixa = tags?.baixaConcorrencia ? tagsP.baixaConcorrencia : true;

      return passCategoria && passStatus && passPreco && passROI && passSazonalidade && passTagAlta && passTagBaixa;
    });
  }, [activeFilters, allProducts]);

  return (
    <Box sx={{ p: 1.5 }}>
      <Typography variant="subtitle1" sx={{ mb: 1 }}>Produtos</Typography>

      {/* Filtros mais compactos */}
      <Box sx={{ "& .MuiFormControl-root": { minWidth: 120, mr: 1, mb: 1 } }}>
        <FiltrosInteligentes
          userId={userId}
          initialFilters={initialFilters}
          onFilter={handleFilter}
          loading={loading}
        />
      </Box>

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 3 }}>
          <CircularProgress size={20} />
        </Box>
      ) : (
        <TableContainer component={Paper} sx={{ mt: 1 }}>
          <Table
            size="small"
            sx={{
              "& td, & th": {
                py: 0.3,
                px: 0.8,
                fontSize: "0.75rem",
                whiteSpace: "nowrap",
              },
            }}
          >
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Img</TableCell>
                <TableCell>Produto</TableCell>
                <TableCell>Cat.</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Preço</TableCell>
                <TableCell align="right">ROI</TableCell>
                <TableCell>Saz.</TableCell>
                <TableCell>Tags</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredProducts.map((p) => {
                const t = computeTags(p);
                return (
                  <TableRow key={p.id} hover>
                    <TableCell>{p.id}</TableCell>
                    <TableCell>
                      {p.imagem ? (
                        <img
                          src={p.imagem}
                          alt={p.nome}
                          style={{
                            width: 28,
                            height: 28,
                            objectFit: "cover",
                            borderRadius: 3,
                          }}
                          loading="lazy"
                        />
                      ) : (
                        <Box sx={{ width: 28, height: 28, bgcolor: "grey.200", borderRadius: 1 }} />
                      )}
                    </TableCell>
                    <TableCell>{p.nome}</TableCell>
                    <TableCell>{p.categoria}</TableCell>
                    <TableCell>{p.status}</TableCell>
                    <TableCell align="right">R$ {p.preco.toFixed(2)}</TableCell>
                    <TableCell align="right">{p.roi.toFixed(2)}x</TableCell>
                    <TableCell>{p.sazonalidade || "-"}</TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", gap: 0.3 }}>
                        {t.altaDemanda && (
                          <Chip size="small" label="Alta" color="primary" sx={{ fontSize: "0.65rem", height: 18 }} />
                        )}
                        {t.baixaConcorrencia && (
                          <Chip size="small" label="Baixa Conc." color="success" sx={{ fontSize: "0.65rem", height: 18 }} />
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                );
              })}
              {filteredProducts.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    Nenhum produto encontrado com os filtros atuais.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
