import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, CheckCircle, Clock, AlertTriangle } from 'lucide-react';
import api from '../services/api';

interface DashboardStats {
    pendientes: number;
    completadas_hoy: number;
    proximas_vencer: number;
    vencidas: number;
    por_prioridad: Record<string, number>;
}

const Dashboard = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/tareas/stats/dashboard');
                setStats(response.data);
            } catch (error) {
                console.error('Error fetching dashboard stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return <div className="text-gray-500">Cargando estadísticas...</div>;
    }

    const statCards = [
        { label: 'Pendientes', value: stats?.pendientes, icon: Clock, color: 'text-blue-600', bg: 'bg-blue-100' },
        { label: 'Completadas Hoy', value: stats?.completadas_hoy, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
        { label: 'Próximas a Vencer', value: stats?.proximas_vencer, icon: Activity, color: 'text-orange-600', bg: 'bg-orange-100' },
        { label: 'Vencidas', value: stats?.vencidas, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100' },
    ];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Panel Principal</h2>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                    Última actualización: {new Date().toLocaleTimeString()}
                </span>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((card, index) => (
                    <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-100 dark:border-gray-700 transition-transform hover:scale-105">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{card.label}</p>
                                <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">{card.value || 0}</p>
                            </div>
                            <div className={`p-3 rounded-lg ${card.bg}`}>
                                <card.icon className={`w-6 h-6 ${card.color}`} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Content Placeholders */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
                    <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Tareas por Prioridad</h3>
                    <div className="space-y-4">
                        {stats?.por_prioridad && Object.entries(stats.por_prioridad).map(([prioridad, count]) => (
                            <div key={prioridad} className="flex items-center justify-between">
                                <span className="capitalize text-gray-600 dark:text-gray-300">{prioridad}</span>
                                <div className="flex-1 mx-4 h-2 bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-blue-500 rounded-full"
                                        style={{ width: `${(count / (stats.pendientes || 1)) * 100}%` }}
                                    ></div>
                                </div>
                                <span className="font-medium text-gray-900 dark:text-white">{count}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-100 dark:border-gray-700">
                    <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Actividad Reciente</h3>
                    <div className="flex items-center justify-center h-48 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-dashed border-gray-200 dark:border-gray-600 text-gray-400">
                        <p>No hay actividad reciente registrada</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
