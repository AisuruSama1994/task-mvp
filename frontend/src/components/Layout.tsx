import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Users, CheckSquare, MessageSquare, History, Settings, UsersRound, Copy } from 'lucide-react';
import { clsx } from 'clsx';

const Layout = () => {
    const navItems = [
        { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/contactos', icon: Users, label: 'Contactos' },
        { to: '/grupos', icon: UsersRound, label: 'Grupos' },
        { to: '/tareas', icon: CheckSquare, label: 'Tareas' },
        { to: '/comunicados', icon: MessageSquare, label: 'Comunicados' },
        { to: '/modelos-comunicados', icon: Copy, label: 'Modelos Comunicados' },
    ];

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                        Task MVP
                    </h1>
                    <p className="text-xs text-gray-500 mt-1">Recordatorios & Tareas</p>
                </div>

                <nav className="flex-1 mt-6 px-4 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            className={({ isActive }) =>
                                clsx(
                                    "flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200",
                                    isActive
                                        ? "bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400 shadow-sm"
                                        : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700/50"
                                )
                            }
                        >
                            <item.icon className={clsx("w-5 h-5 mr-3", ({ isActive }: any) => isActive ? "text-blue-600" : "text-gray-500")} />
                            {item.label}
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center px-4 py-2 text-xs text-gray-500 dark:text-gray-400">
                        <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                        Sistema Online
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="p-8 max-w-7xl mx-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default Layout;
