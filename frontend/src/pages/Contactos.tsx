import React, { useEffect, useState } from 'react';
import { Plus, Search, Edit2, Trash2, Mail, Phone, Tag } from 'lucide-react';
import api from '../services/api';
import type { Contacto } from '../types';
import Modal from '../components/Modal';

const Contactos = () => {
    const [contactos, setContactos] = useState<Contacto[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    // Modal State
    const [showModal, setShowModal] = useState(false);
    const [editingContacto, setEditingContacto] = useState<Contacto | null>(null);
    const [verifyDelete, setVerifyDelete] = useState<string | null>(null);

    // Form State
    const [formData, setFormData] = useState({
        nombre: '',
        email: '',
        whatsapp: '',
        etiquetas: '',
        notas: ''
    });

    const fetchContactos = async (searchTerm = '') => {
        try {
            const response = await api.get(`/contactos?search=${searchTerm}`);
            setContactos(response.data);
        } catch (error) {
            console.error('Error fetching contactos:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            fetchContactos(search);
        }, 300);
        return () => clearTimeout(timeoutId);
    }, [search]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const payload = {
                ...formData,
                etiquetas: formData.etiquetas.split(',').map(tag => tag.trim()).filter(Boolean)
            };

            if (editingContacto) {
                await api.put(`/contactos/${editingContacto.id}`, payload);
            } else {
                await api.post('/contactos', payload);
            }

            setShowModal(false);
            resetForm();
            fetchContactos(search);
        } catch (error) {
            console.error('Error saving contacto:', error);
            alert('Error al guardar el contacto. Verifica los datos.');
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await api.delete(`/contactos/${id}`);
            setVerifyDelete(null);
            fetchContactos(search);
        } catch (error) {
            console.error('Error deleting contacto:', error);
        }
    };

    const openEdit = (contacto: Contacto) => {
        setEditingContacto(contacto);
        setFormData({
            nombre: contacto.nombre,
            email: contacto.email || '',
            whatsapp: contacto.whatsapp || '',
            etiquetas: contacto.etiquetas.join(', '),
            notas: contacto.notas || ''
        });
        setShowModal(true);
    };

    const resetForm = () => {
        setEditingContacto(null);
        setFormData({
            nombre: '',
            email: '',
            whatsapp: '',
            etiquetas: '',
            notas: ''
        });
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Contactos</h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">Gestiona tus destinatarios</p>
                </div>
                <button
                    onClick={() => { resetForm(); setShowModal(true); }}
                    className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    Nuevo Contacto
                </button>
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                    type="text"
                    placeholder="Buscar por nombre, email o whatsapp..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                />
            </div>

            {/* Table */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 dark:bg-gray-700/50">
                            <tr>
                                <th className="p-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Nombre</th>
                                <th className="p-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Contacto</th>
                                <th className="p-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Etiquetas</th>
                                <th className="p-4 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider text-right">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {loading ? (
                                <tr>
                                    <td colSpan={4} className="p-8 text-center text-gray-500">Cargando contactos...</td>
                                </tr>
                            ) : contactos.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="p-8 text-center text-gray-500">No se encontraron contactos.</td>
                                </tr>
                            ) : (
                                contactos.map((contacto) => (
                                    <tr key={contacto.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
                                        <td className="p-4">
                                            <div className="font-medium text-gray-900 dark:text-white">{contacto.nombre}</div>
                                            {contacto.notas && (
                                                <div className="text-xs text-gray-500 truncate max-w-[200px]">{contacto.notas}</div>
                                            )}
                                        </td>
                                        <td className="p-4">
                                            <div className="space-y-1">
                                                {contacto.email && (
                                                    <div className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                                                        <Mail className="w-3 h-3 mr-2 text-gray-400" />
                                                        {contacto.email}
                                                    </div>
                                                )}
                                                {contacto.whatsapp && (
                                                    <div className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                                                        <Phone className="w-3 h-3 mr-2 text-gray-400" />
                                                        {contacto.whatsapp}
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex flex-wrap gap-1">
                                                {contacto.etiquetas.map((tag, idx) => (
                                                    <span key={idx} className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border border-blue-100 dark:border-blue-800">
                                                        <Tag className="w-3 h-3 mr-1" />
                                                        {tag}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="p-4 text-right">
                                            <div className="flex justify-end space-x-2">
                                                <button
                                                    onClick={() => openEdit(contacto)}
                                                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-500 dark:text-gray-400 transition-colors"
                                                >
                                                    <Edit2 className="w-4 h-4" />
                                                </button>
                                                {verifyDelete === contacto.id ? (
                                                    <button
                                                        onClick={() => handleDelete(contacto.id)}
                                                        className="p-2 bg-red-100 dark:bg-red-900/30 text-red-600 rounded-lg text-xs font-bold"
                                                    >
                                                        ¿Borrar?
                                                    </button>
                                                ) : (
                                                    <button
                                                        onClick={() => setVerifyDelete(contacto.id)}
                                                        className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg text-gray-500 hover:text-red-500 transition-colors"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal Crear/Editar */}
            <Modal
                isOpen={showModal}
                onClose={() => setShowModal(false)}
                title={editingContacto ? "Editar Contacto" : "Nuevo Contacto"}
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Nombre Completo
                        </label>
                        <input
                            type="text"
                            required
                            value={formData.nombre}
                            onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                            className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="Ej. Juan Pérez"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Email
                            </label>
                            <input
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="juan@ejemplo.com"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                WhatsApp
                            </label>
                            <input
                                type="text"
                                value={formData.whatsapp}
                                onChange={(e) => setFormData({ ...formData, whatsapp: e.target.value })}
                                className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                placeholder="+54911..."
                            />
                            <p className="text-xs text-gray-500 mt-1">Formato internacional ej: +549...</p>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Etiquetas
                        </label>
                        <input
                            type="text"
                            value={formData.etiquetas}
                            onChange={(e) => setFormData({ ...formData, etiquetas: e.target.value })}
                            className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="cliente, vip, proveedor (separadas por coma)"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Notas
                        </label>
                        <textarea
                            rows={3}
                            value={formData.notas}
                            onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                            className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="Información adicional..."
                        />
                    </div>

                    <div className="flex justify-end space-x-3 mt-6">
                        <button
                            type="button"
                            onClick={() => setShowModal(false)}
                            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
                        >
                            {editingContacto ? 'Guardar Cambios' : 'Crear Contacto'}
                        </button>
                    </div>
                </form>
            </Modal>
        </div>
    );
};

export default Contactos;
