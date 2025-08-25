import React, { useEffect, useState } from 'react';
import AnimatedCard from '../components/AnimatedCard';
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
});

export default function OAuthManager() {
  const [endpoints, setEndpoints] = useState([]);

  useEffect(() => {
    loadEndpoints();
  }, []);

  async function loadEndpoints() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('Nenhum token encontrado no localStorage.');
        return;
      }
      const r = await api.get('/api/endpoints', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEndpoints(r.data);
    } catch (e) {
      console.error('Erro ao carregar endpoints', e);
      setEndpoints([]);
    }
  }

  async function startOAuth(id) {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Você precisa estar logado para iniciar o OAuth.');
        return;
      }
      const r = await api.post(`/api/oauth/start?endpoint_id=${id}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      window.open(r.data.authorization_url, '_blank');
      alert('Abra a aba e conclua o fluxo. Depois volte ao painel.');
    } catch (e) {
      console.error('Erro ao iniciar OAuth', e);
      alert('Falha ao iniciar o fluxo OAuth.');
    }
  }

  function handleConnect() {
    window.location.href = `${import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'}/api/oauth/login`;
  }

  return (
    <div className="p-8 max-w-lg mx-auto space-y-6">
      {/* Botão para conectar Mercado Livre */}
      <div>
        <h1 className="text-xl font-bold mb-4">Conectar Mercado Libre</h1>
        <button
          onClick={handleConnect}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Conectar Mercado Libre
        </button>
        <p className="mt-4 text-sm text-gray-500">
          Ao conectar, você será redirecionado para autorizar.
        </p>
      </div>

      {/* Lista de endpoints para gerenciar OAuth */}
      <AnimatedCard title="Gerenciar OAuth">
        <div className="space-y-2">
          <p className="text-sm">
            Selecione uma integração e inicie o fluxo OAuth com Mercado Libre.
          </p>
          <div className="space-y-2 mt-2">
            {endpoints.length > 0 ? (
              endpoints.map((ep) => (
                <div
                  key={ep.id}
                  className="flex items-center justify-between bg-slate-50 p-2 rounded"
                >
                  <div>{ep.name}</div>
                  <button
                    className="px-3 py-1 bg-emerald-500 text-white rounded"
                    onClick={() => startOAuth(ep.id)}
                  >
                    Conectar
                  </button>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-400">Nenhum endpoint disponível.</p>
            )}
          </div>
        </div>
      </AnimatedCard>
    </div>
  );
}
