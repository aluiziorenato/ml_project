import { useEffect, useState, useCallback } from "react";

export function useFilterOptions() {
  const [categorias, setCategorias] = useState<string[]>([]);
  const [status, setStatus] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchOptions = useCallback(async () => {
    setLoading(true);
    try {
      // MOCK atual — trocamos por chamada de API depois
      await new Promise((r) => setTimeout(r, 200));
      setCategorias(["Eletrônicos", "Casa", "Moda", "Beleza", "Esporte"]);
      setStatus(["Ativo", "Pausado", "Esgotado", "Oculto"]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOptions();
  }, [fetchOptions]);

  return { categorias, status, loading, fetchOptions };
}
