import React, {useState} from 'react'
import AnimatedCard from '../components/AnimatedCard'
import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' })

export default function ApiTester(){
  const [path, setPath] = useState('/users/me')
  const [method, setMethod] = useState('GET')
  const [response, setResponse] = useState(null)

  async function run(){
    try{
      const token = localStorage.getItem('access_token')
      const r = await api.post('/api/proxy', { endpoint_id: 1, method, path }, { headers: { Authorization: `Bearer ${token}` } })
      setResponse(r.data)
    }catch(e){
      setResponse({error: e.message})
    }
  }

  return (
    <AnimatedCard title="API Tester">
      <div className="space-y-3">
        <div className="flex gap-2">
          <select value={method} onChange={e=>setMethod(e.target.value)} className="p-2 border rounded">
            <option>GET</option>
            <option>POST</option>
            <option>PUT</option>
            <option>DELETE</option>
          </select>
          <input className="flex-1 p-2 border rounded" value={path} onChange={e=>setPath(e.target.value)} />
          <button className="px-3 py-2 bg-indigo-600 text-white rounded" onClick={run}>Enviar</button>
        </div>
        {response && <pre className="bg-slate-100 p-3 rounded">{JSON.stringify(response, null, 2)}</pre>}
      </div>
    </AnimatedCard>
  )
}
