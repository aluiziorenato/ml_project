import React, {useEffect, useState} from 'react'
import AnimatedCard from '../components/AnimatedCard'
import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' })

export default function OAuthManager(){
  const [endpoints, setEndpoints] = useState([])
  useEffect(()=>{ load() },[])
  async function load(){
    try{
      const token = localStorage.getItem('access_token')
      const r = await api.get('/api/endpoints', { headers: { Authorization: `Bearer ${token}` } })
      setEndpoints(r.data)
    }catch(e){ setEndpoints([]) }
  }
  async function startOAuth(id){
    const token = localStorage.getItem('access_token')
    const r = await api.post(`/api/oauth/start?endpoint_id=${id}`, {}, { headers: { Authorization: `Bearer ${token}` } })
    window.open(r.data.authorization_url, '_blank')
    alert('Abra a aba e conclua o fluxo. Volte ao painel.')
  }

  return (
    <AnimatedCard title="Gerenciar OAuth">
      <div className="space-y-2">
        <p className="text-sm">Selecione uma integração e inicie o fluxo OAuth com Mercado Libre.</p>
        <div className="space-y-2 mt-2">
          {endpoints.map(ep => (
            <div key={ep.id} className="flex items-center justify-between bg-slate-50 p-2 rounded">
              <div>{ep.name}</div>
              <button className="px-3 py-1 bg-emerald-500 text-white rounded" onClick={()=>startOAuth(ep.id)}>Conectar</button>
            </div>
          ))}
        </div>
      </div>
    </AnimatedCard>
  )
}
