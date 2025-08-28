import React, { useEffect, useState } from "react";
import AnimatedCard from "./AnimatedCard";
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
});

interface Endpoint {
  name: string;
  base_url: string;
  auth_type: string;
  [key: string]: any;
}

const ApiConfig: React.FC = () => {
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
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
        {/* Renderize endpoints e botões conforme necessário */}
        {/* ...existing code... */}
      </div>
    </AnimatedCard>
  );
};

export default ApiConfig;
