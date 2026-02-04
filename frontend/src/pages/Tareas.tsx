import React, { useEffect, useState } from 'react';
import { Plus, Search, Edit2, Trash2, Calendar } from 'lucide-react';
import api from '../services/api';
import type { Tarea } from '../types';
import Modal from '../components/Modal';

interface TareaForm {
  titulo: string;
  descripcion: string;
  fecha_creacion: string;
  fecha_termino: string;
  prioridad: string;
  estado: string;
  etiquetas: string;
}

const Tareas = () => {
  const [tareas, setTareas] = useState<(Tarea & { urgencia?: string; dias_restantes?: number })[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterEstado, setFilterEstado] = useState('');
  const [filterPrioridad, setFilterPrioridad] = useState('');

  const [showModal, setShowModal] = useState(false);
  const [editingTarea, setEditingTarea] = useState<Tarea | null>(null);
  const [verifyDelete, setVerifyDelete] = useState<string | null>(null);

  const [formData, setFormData] = useState<TareaForm>({
    titulo: '',
    descripcion: '',
    fecha_creacion: new Date().toISOString().split('T')[0],
    fecha_termino: '',
    prioridad: 'media',
    estado: 'pendiente',
    etiquetas: ''
  });

  const fetchTareas = async () => {
    try {
      const response = await api.get('/tareas/con-urgencia');
      setTareas(response.data);
    } catch (error) {
      console.error('Error fetching tareas:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTareas();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        etiquetas: formData.etiquetas.split(',').map(tag => tag.trim()).filter(Boolean)
      };

      if (editingTarea) {
        await api.put(`/tareas/${editingTarea.id}`, payload);
      } else {
        await api.post('/tareas', payload);
      }

      setShowModal(false);
      resetForm();
      fetchTareas();
    } catch (error) {
      console.error('Error saving tarea:', error);
      alert('Error al guardar la tarea');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/tareas/${id}`);
      setVerifyDelete(null);
      fetchTareas();
    } catch (error) {
      console.error('Error deleting tarea:', error);
    }
  };

  const handleChangeEstado = async (id: string, nuevoEstado: string) => {
    try {
      await api.put(`/tareas/${id}/estado`, {
        nuevo_estado: nuevoEstado,
        usuario: 'sistema'
      });
      fetchTareas();
    } catch (error) {
      console.error('Error changing estado:', error);
    }
  };

  const openEdit = (tarea: Tarea) => {
    setEditingTarea(tarea);
    setFormData({
      titulo: tarea.titulo,
      descripcion: tarea.descripcion || '',
      fecha_creacion: tarea.fecha_creacion,
      fecha_termino: tarea.fecha_termino || '',
      prioridad: tarea.prioridad,
      estado: tarea.estado,
      etiquetas: tarea.etiquetas.join(', ')
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setEditingTarea(null);
    setFormData({
      titulo: '',
      descripcion: '',
      fecha_creacion: new Date().toISOString().split('T')[0],
      fecha_termino: '',
      prioridad: 'media',
      estado: 'pendiente',
      etiquetas: ''
    });
  };

  const getUrgenciaColor = (urgencia?: string) => {
    switch (urgencia) {
      case 'vencida':
        return 'bg-red-100 text-red-800';
      case 'hoy':
        return 'bg-orange-100 text-orange-800';
      case 'urgente':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  const getPrioridadColor = (prioridad: string) => {
    switch (prioridad) {
      case 'urgente': return 'text-red-600';
      case 'alta': return 'text-orange-600';
      case 'media': return 'text-blue-600';
      default: return 'text-green-600';
    }
  };

  const filteredTareas = tareas.filter(t => {
    const matchSearch = t.titulo.toLowerCase().includes(search.toLowerCase());
    const matchEstado = !filterEstado || t.estado === filterEstado;
    const matchPrioridad = !filterPrioridad || t.prioridad === filterPrioridad;
    return matchSearch && matchEstado && matchPrioridad;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Tareas</h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Gestiona tus tareas y recordatorios</p>
        </div>
        <button
          onClick={() => { resetForm(); setShowModal(true); }}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nueva Tarea
        </button>
      </div>

      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Buscar tareas..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <select value={filterEstado} onChange={(e) => setFilterEstado(e.target.value)} className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-800">
            <option value="">Todos los estados</option>
            <option value="pendiente">Pendiente</option>
            <option value="en_progreso">En Progreso</option>
            <option value="completada">Completada</option>
            <option value="cancelada">Cancelada</option>
          </select>

          <select value={filterPrioridad} onChange={(e) => setFilterPrioridad(e.target.value)} className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-800">
            <option value="">Todas las prioridades</option>
            <option value="baja">Baja</option>
            <option value="media">Media</option>
            <option value="alta">Alta</option>
            <option value="urgente">Urgente</option>
          </select>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th className="p-4 text-left text-sm font-medium">Título</th>
              <th className="p-4 text-left text-sm font-medium">Prioridad</th>
              <th className="p-4 text-left text-sm font-medium">Vencimiento</th>
              <th className="p-4 text-left text-sm font-medium">Urgencia</th>
              <th className="p-4 text-left text-sm font-medium">Estado</th>
              <th className="p-4 text-right text-sm font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <tr><td colSpan={6} className="p-8 text-center text-gray-500">Cargando...</td></tr>
            ) : filteredTareas.length === 0 ? (
              <tr><td colSpan={6} className="p-8 text-center text-gray-500">No hay tareas</td></tr>
            ) : (
              filteredTareas.map((tarea) => (
                <tr key={tarea.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="p-4">
                    <div className="font-medium">{tarea.titulo}</div>
                    {tarea.descripcion && <p className="text-sm text-gray-600 truncate">{tarea.descripcion}</p>}
                  </td>
                  <td className="p-4 text-sm"><span className={getPrioridadColor(tarea.prioridad)}>{tarea.prioridad}</span></td>
                  <td className="p-4 text-sm">
                    {tarea.fecha_termino ? new Date(tarea.fecha_termino).toLocaleDateString('es-AR') : '-'}
                  </td>
                  <td className="p-4">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getUrgenciaColor(tarea.urgencia)}`}>
                      {tarea.urgencia === 'vencida' && '🔴 Vencida'}
                      {tarea.urgencia === 'hoy' && '🟠 Hoy'}
                      {tarea.urgencia === 'urgente' && '🟡 Urgente'}
                      {tarea.urgencia === 'normal' && '🟢 Normal'}
                      {tarea.urgencia === 'sin_fecha' && '⚪ Sin fecha'}
                    </span>
                  </td>
                  <td className="p-4">
                    <select value={tarea.estado} onChange={(e) => handleChangeEstado(tarea.id, e.target.value)} className="px-2 py-1 border rounded text-sm bg-white dark:bg-gray-700">
                      <option value="pendiente">Pendiente</option>
                      <option value="en_progreso">En Progreso</option>
                      <option value="completada">Completada</option>
                      <option value="cancelada">Cancelada</option>
                    </select>
                  </td>
                  <td className="p-4 text-right flex justify-end gap-2">
                    <button onClick={() => openEdit(tarea)} className="text-blue-600 hover:text-blue-700">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => setVerifyDelete(tarea.id)} className="text-red-600 hover:text-red-700">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editingTarea ? 'Editar Tarea' : 'Nueva Tarea'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input required value={formData.titulo} onChange={(e) => setFormData({...formData, titulo: e.target.value})} placeholder="Título" className="w-full p-2 border rounded bg-white dark:bg-gray-700" />
          <textarea value={formData.descripcion} onChange={(e) => setFormData({...formData, descripcion: e.target.value})} placeholder="Descripción" className="w-full p-2 border rounded bg-white dark:bg-gray-700" rows={3} />
          <div className="grid grid-cols-2 gap-4">
            <input type="date" value={formData.fecha_creacion} onChange={(e) => setFormData({...formData, fecha_creacion: e.target.value})} className="w-full p-2 border rounded bg-white dark:bg-gray-700" />
            <input type="date" value={formData.fecha_termino} onChange={(e) => setFormData({...formData, fecha_termino: e.target.value})} className="w-full p-2 border rounded bg-white dark:bg-gray-700" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <select value={formData.prioridad} onChange={(e) => setFormData({...formData, prioridad: e.target.value})} className="w-full p-2 border rounded bg-white dark:bg-gray-700">
              <option value="baja">Baja</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
              <option value="urgente">Urgente</option>
            </select>
            <select value={formData.estado} onChange={(e) => setFormData({...formData, estado: e.target.value})} className="w-full p-2 border rounded bg-white dark:bg-gray-700">
              <option value="pendiente">Pendiente</option>
              <option value="en_progreso">En Progreso</option>
              <option value="completada">Completada</option>
              <option value="cancelada">Cancelada</option>
            </select>
          </div>
          <input value={formData.etiquetas} onChange={(e) => setFormData({...formData, etiquetas: e.target.value})} placeholder="Etiquetas (comas)" className="w-full p-2 border rounded bg-white dark:bg-gray-700" />
          <div className="flex gap-2 pt-4">
            <button type="submit" className="flex-1 bg-blue-600 text-white p-2 rounded hover:bg-blue-700">Guardar</button>
            <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-gray-300 dark:bg-gray-600 p-2 rounded">Cancelar</button>
          </div>
        </form>
      </Modal>

      {verifyDelete && <Modal isOpen onClose={() => setVerifyDelete(null)} title="Confirmar">
        <p className="mb-4">¿Eliminar esta tarea?</p>
        <div className="flex gap-2">
          <button onClick={() => handleDelete(verifyDelete)} className="flex-1 bg-red-600 text-white p-2 rounded">Eliminar</button>
          <button onClick={() => setVerifyDelete(null)} className="flex-1 bg-gray-300 dark:bg-gray-600 p-2 rounded">Cancelar</button>
        </div>
      </Modal>}
    </div>
  );
};

export default Tareas;
