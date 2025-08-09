import React, {useEffect, useState} from 'react'
import LineChartCard from '../components/Charts/LineChartCard'

export default function Dashboard(){
  const [data, setData] = useState([])
  useEffect(()=>{
    const d = Array.from({length:12}).map((_,i)=>({label:`M${i+1}`, value: Math.round(Math.random()*200)}))
    setData(d)
  },[])

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <LineChartCard title="Requests por mês" data={data} />
        <LineChartCard title="Erros por mês" data={data.map(x=>({label:x.label, value: Math.round(x.value*Math.random())}))} />
      </div>
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-1">
          <div className="bg-white rounded-2xl p-4 shadow-md">
            <h4 className="font-semibold">Conexões Ativas</h4>
            <div className="text-3xl mt-2">3</div>
          </div>
        </div>
        <div>
          <div className="bg-white rounded-2xl p-4 shadow-md">
            <h4 className="font-semibold">Requests Última Hora</h4>
            <div className="text-3xl mt-2">124</div>
          </div>
        </div>
        <div>
          <div className="bg-white rounded-2xl p-4 shadow-md">
            <h4 className="font-semibold">Tokens expirando</h4>
            <div className="text-3xl mt-2">1</div>
          </div>
        </div>
      </div>
    </div>
  )
}
