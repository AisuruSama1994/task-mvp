import React, { useEffect, useState } from 'react';
import { Plus, Search, Edit2, Trash2, Users, Mail, MessageSquare } from 'lucide-react';
import api from '../services/api';
import type { Grupo, Contacto } from '../types';
import Modal from '../components/Modal';

interface GrupoForm {
  nombre: string;
  descripcion: string;
  tipo: string;
  estado: string;
}

const Grupos = () => {
  const [grupos, setGrupos] = useState<Grupo[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingGrupo, setEditingGrupo] = useState<Grupo | null>(null);
  const [verifyDelete, setVerifyDelete] = useState<string | null>(null);
  const [showMiembros, setShowMiembros] = useState<string | null>(null);
  const [miembros, setMiembros] = useState<Contacto[]>([]);

  const [formData, setFormData] = useState<GrupoForm>({
    nombre: '',
    descripcion: '',
    tipo: 'email',
    estado: 'activo'
  });

  const fetchGrupos = async () => {
    try {
      const response = await api.get('/grupos');
      setGrupos(response.data);
    } catch (error) {
      console.error('Error fetching grupos:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMiembros = async (grupoId: string) => {
    try {
      const response = await api.get(`/grupos/${grupoId}/miembros`);
      setMiembros(response.data);
      setShowMiembros(grupoId);
    } catch (error) {
      console.error('Error fetching miembros:', error);
    }
  };

  useEffect(() => {
    fetchGrupos();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingGrupo) {
        await api.put(`/grupos/${editingGrupo.id}`, formData);
      } else {
        await api.post('/grupos', formData);
      }
      setShowModal(false);
      resetForm();
      fetchGrupos();
    } catch (error) {
      console.error('Error saving grupo:', error);
      alert('Error al guardar el grupo');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/grupos/${id}`);
      setVerifyDelete(null);
      fetchGrupos();
    } catch (error) {
      console.error('Error deleting grupo:', error);
    }
  };

  const openEdit = (grupo: Grupo) => {
    setEditingGrupo(grupo);
    setFormData({
      nombre: grupo.nombre,
      descripcion: grupo.descripcion || '',
      tipo: grupo.tipo,
      estado: grupo.estado
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setEditingGrupo(null);
    setFormData({
      nombre: '',
      descripcion: '',
      tipo: 'email',
      estado: 'activo'
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Grupos</h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Organiza tus contactos en grupos</p>
        </div>
        <button
          onClick={() => { resetForm(); setShowModal(true); }}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nuevo Grupo
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Buscar grupos..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
        />
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="p-4 text-left text-sm font-medium text-gray-700 dark:text-gray-300">Nombre</th>
                <th className="p-4 text-left text-sm font-medium text-gray-700 dark:text-gray-300">Tipo</th>
                <th className="p-4 text-left text-sm font-medium text-gray-700 dark:text-gray-300">Miembros</th>
                <th className="p-4 text-right text-sm font-medium text-gray-700 dark:text-gray-300">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {loading ? (
                <tr><td colSpan={4} className="p-8 text-center text-gray-500">Cargando...</td></tr>
              ) : grupos.length === 0 ? (
                <tr><td colSpan={4} className="p-8 text-center text-gray-500">No hay grupos</td></tr>
              ) : (
                grupos.map((grupo) => (
                  <tr key={grupo.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                    <td className="p-4 font-medium text-gray-900 dark:text-white">{grupo.nombre}</td>
                    <td className="p-4 text-sm text-gray-600 dark:text-gray-400">{grupo.tipo}</td>
                    <td className="p-4">
                      <button onClick={() => fetchMiembros(grupo.id)} className="text-blue-600 dark:text-blue-400 hover:text-blue-700">
                        <Users className="w-4 h-4" />
                      </button>
                    </td>
                    <td className="p-4 text-right flex justify-end gap-2">
                      <button onClick={() => openEdit(grupo)} className="text-blue-600 dark:text-blue-400 hover:text-blue-700">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button onClick={() => setVerifyDelete(grupo.id)} className="text-red-600 dark:text-red-400 hover:text-red-700">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editingGrupo ? 'Editar Grupo' : 'Nuevo Grupo'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            required
            value={formData.nombre}
            onChange={(e) => setFormData({...formData, nombre: e.target.value})}
            placeholder="Nombre del grupo"
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
          />
          <textarea
            value={formData.descripcion}
            onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
            placeholder="Descripción"
            className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
            rows={3}
          />
          <select value={formData.tipo} onChange={(e) => setFormData({...formData, tipo: e.target.value})} className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700">
            <option value="email">Email</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="ambos">Ambos</option>
          </select>
          <div className="flex gap-2">
            <button type="submit" className="flex-1 bg-blue-600 text-white p-2 rounded hover:bg-blue-700">Guardar</button>
            <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-gray-300 dark:bg-gray-600 p-2 rounded hover:bg-gray-400">Cancelar</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={showMiembros !== null} onClose={() => setShowMiembros(null)} title="Miembros del Grupo">
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {miembros.length === 0 ? (
            <p className="text-gray-500">No hay miembros en este grupo</p>
          ) : (
            miembros.map(m => (
              <div key={m.id} className="p-2 bg-gray-100 dark:bg-gray-700 rounded">
                <p className="font-medium">{m.nombre}</p>
                <p className="text-sm text-gray-600">{m.email}</p>
              </div>
            ))
          )}
        </div>
      </Modal>

      {verifyDelete && (
        <Modal isOpen onClose={() => setVerifyDelete(null)} title="Confirmar eliminación">
          <p className="mb-4 text-gray-600 dark:text-gray-300">¿Estás seguro de eliminar este grupo?</p>
          <div className="flex gap-2">
            <button onClick={() => handleDelete(verifyDelete)} className="flex-1 bg-red-600 text-white p-2 rounded hover:bg-red-700">Eliminar</button>
            <button onClick={() => setVerifyDelete(null)} className="flex-1 bg-gray-300 dark:bg-gray-600 p-2 rounded">Cancelar</button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Grupos;
