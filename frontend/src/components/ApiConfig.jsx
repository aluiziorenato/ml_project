import React, { useEffect, useState } from "react";
import AnimatedCard from "./AnimatedCard";
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
});

export default function ApiConfig() {
  const [endpoints, setEndpoints] = useState([]);
  const [name, setName] = useState("");
  const [baseUrl, setBaseUrl] = useState("https://api.mercadolibre.com");

  useEffect(() => {
    reload();
  }, []);

  const reload = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await api.get("/api/endpoints", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEndpoints(response.data);
    } catch (error) {
      setEndpoints([]);
    }
  };

  const addIntegration = async () => {
    const token = localStorage.getItem("access_token");
    await api.post(
      "/api/endpoints",
      {
        name,
        base_url: baseUrl,
        auth_type: "oauth2",
      },
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    setName("");
    reload();
  };

  return (
    <AnimatedCard title="Configurações de API">
      <div className="space-y-3">
        <input
          className="w-full p-2 border rounded"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome da integração"
        />
        <input
          className="w-full p-2 border rounded"
          value={baseUrl}
          onChange={(e) => setBaseUrl(e.target.value)}
          placeholder="Base URL"
        />
        <div className="flex gap-2">
          <button
            className="px-4 py-2 bg-indigo-600 text-white rounded"
            onClick={addIntegration}
          >
            Adicionar
          </button>
        </div>
        <div className="mt-3">
          <h4 className="font-semibold">Integrações</h4>
          <ul className="mt-2 space-y-2">
            {endpoints.map((ep) => (
              <li key={ep.id} className="bg-slate-50 p-3 rounded">
                {ep.name} — {ep.base_url}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </AnimatedCard>
  );
}
