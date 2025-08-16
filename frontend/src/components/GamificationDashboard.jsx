import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const api = axios.create({ 
    baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
});

const GamificationDashboard = ({ userId }) => {
    const [achievements, setAchievements] = useState([]);
    const [badges, setBadges] = useState([]);
    const [ranking, setRanking] = useState(null);
    const [leaderboard, setLeaderboard] = useState([]);
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
            console.error('Erro ao carregar dados de gamificação:', error);
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
            {/* User Stats Summary */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-6 text-white"
            >
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center">
                        <div className="text-3xl font-bold">{ranking?.total_points || 0}</div>
                        <div className="text-sm opacity-90">Pontos Totais</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl font-bold">#{ranking?.rank_position || '-'}</div>
                        <div className="text-sm opacity-90">Posição no Ranking</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl font-bold">{achievements.length}</div>
                        <div className="text-sm opacity-90">Conquistas</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl font-bold">{badges.length}</div>
                        <div className="text-sm opacity-90">Emblemas</div>
                    </div>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Achievements */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                >
                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                        🏆 Conquistas Recentes
                    </h3>
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                        {achievements.slice(0, 5).map((achievement) => (
                            <motion.div
                                key={achievement.id}
                                whileHover={{ scale: 1.02 }}
                                className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
                            >
                                <div className="text-2xl">{achievement.icon}</div>
                                <div className="flex-1">
                                    <div className="font-medium">{achievement.title}</div>
                                    <div className="text-sm text-gray-600">{achievement.description}</div>
                                    <div className="text-xs text-indigo-600">+{achievement.points} pontos</div>
                                </div>
                            </motion.div>
                        ))}
                        {achievements.length === 0 && (
                            <div className="text-center text-gray-500 py-4">
                                Nenhuma conquista ainda
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Badges Collection */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                >
                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                        🎖️ Coleção de Emblemas
                    </h3>
                    <div className="grid grid-cols-3 gap-3 max-h-64 overflow-y-auto">
                        {badges.map((badge) => (
                            <motion.div
                                key={badge.id}
                                whileHover={{ scale: 1.1 }}
                                className="text-center p-3 bg-gray-50 rounded-lg relative"
                            >
                                <div className="text-3xl mb-2">{badge.icon}</div>
                                <div className="text-xs font-medium">{badge.title}</div>
                                <div className="text-xs text-gray-600">Nível {badge.level}</div>
                                {badge.level > 1 && (
                                    <div className="absolute -top-1 -right-1 bg-yellow-400 text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                                        {badge.level}
                                    </div>
                                )}
                            </motion.div>
                        ))}
                        {badges.length === 0 && (
                            <div className="col-span-3 text-center text-gray-500 py-4">
                                Nenhum emblema ainda
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Leaderboard */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                >
                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                        🥇 Ranking Global
                    </h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {leaderboard.map((user, index) => (
                            <motion.div
                                key={user.id}
                                whileHover={{ scale: 1.02 }}
                                className={`flex items-center space-x-3 p-2 rounded-lg ${
                                    user.user_id === userId ? 'bg-indigo-100 border border-indigo-300' : 'bg-gray-50'
                                }`}
                            >
                                <div className={`font-bold text-lg ${
                                    index === 0 ? 'text-yellow-500' :
                                    index === 1 ? 'text-gray-400' :
                                    index === 2 ? 'text-orange-500' : 'text-gray-600'
                                }`}>
                                    #{user.rank_position}
                                </div>
                                <div className="flex-1">
                                    <div className="font-medium">{user.username}</div>
                                    <div className="text-sm text-gray-600">
                                        {user.total_points} pts • Nível {user.level}
                                    </div>
                                </div>
                                {index < 3 && (
                                    <div className="text-xl">
                                        {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                                    </div>
                                )}
                            </motion.div>
                        ))}
                        {leaderboard.length === 0 && (
                            <div className="text-center text-gray-500 py-4">
                                Ranking vazio
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>

            {/* Progress to Next Level */}
            {ranking && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                >
                    <h3 className="text-lg font-semibold mb-4">Progresso para o Próximo Nível</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span>Nível {ranking.level}</span>
                            <span>Nível {ranking.level + 1}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ 
                                    width: `${Math.min(100, (ranking.experience % 1000) / 10)}%` 
                                }}
                                transition={{ duration: 1, ease: "easeOut" }}
                                className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full"
                            />
                        </div>
                        <div className="text-center text-sm text-gray-600">
                            {ranking.experience % 1000} / 1000 XP
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    );
};

export default GamificationDashboard;