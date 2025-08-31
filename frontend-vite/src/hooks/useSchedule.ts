import { useState, useEffect } from 'react';
import { ScheduleCell } from './HeatmapCell';

export function useSchedule(apiGet: string, apiPatch: string) {
  const [schedule, setSchedule] = useState<ScheduleCell[][]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSchedule() {
      setLoading(true);
      try {
        // const res = await fetch(apiGet);
        // const data = await res.json();
        // setSchedule(data.schedule);
        // Simulação inicial
        const days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
        const hours = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'];
        const mock = hours.map((hour) =>
          days.map((day) => ({
            day,
            hour,
            active: Math.random() > 0.5,
            intensity: Math.floor(Math.random() * 100),
            lastUpdate: '2025-08-30 09:00',
          }))
        );
        setSchedule(mock);
      } catch (err) {
        setError('Erro ao carregar dados do backend.');
      }
      setLoading(false);
    }
    fetchSchedule();
  }, [apiGet]);

  async function saveSchedule() {
    setSaving(true);
    setSuccess(null);
    setError(null);
    try {
      // await fetch(apiPatch, { method: 'PATCH', body: JSON.stringify({ schedule }) });
      setSuccess('Alterações salvas com sucesso!');
    } catch (err) {
      setError('Erro ao salvar alterações.');
    }
    setSaving(false);
  }

  return { schedule, setSchedule, loading, saving, error, success, saveSchedule };
}
