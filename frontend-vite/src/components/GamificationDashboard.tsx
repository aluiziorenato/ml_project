import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const api = axios.create({ 
    baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
});

interface GamificationDashboardProps {
  userId: string;
}

const GamificationDashboard: React.FC<GamificationDashboardProps> = ({ userId }) => {
  const [achievements, setAchievements] = useState<any[]>([]);
  const [badges, setBadges] = useState<any[]>([]);
  const [ranking, setRanking] = useState<any>(null);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      loadGamificationData();
    }
  }, [userId]);

  const loadGamificationData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      const [achievementsRes, badgesRes, rankingRes, leaderboardRes] = await Promise.all([
        axios.get(`http://localhost:8018/achievements/${userId}`, { headers }),
        axios.get(`http://localhost:8018/badges/${userId}`, { headers }),
        axios.get(`http://localhost:8018/ranking/${userId}`, { headers }),
        axios.get(`http://localhost:8018/leaderboard?limit=10&user_id=${userId}`, { headers })
      ]);
      setAchievements(achievementsRes.data);
      setBadges(badgesRes.data);
      setRanking(rankingRes.data);
      setLeaderboard(leaderboardRes.data.rankings);
    } catch (error) {
      // Trate o erro conforme necessário
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Renderize o dashboard de gamificação conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default GamificationDashboard;
