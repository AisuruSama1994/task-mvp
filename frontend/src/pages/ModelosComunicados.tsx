import React, { useEffect, useState } from 'react';
import { Plus, Search, Edit2, Trash2, Copy } from 'lucide-react';
import api from '../services/api';
import Modal from '../components/Modal';

interface Modelo {
  id: string;
  nombre: string;
  descripcion: string;
  tipo: string;
  contenido: string;
}

interface ModeloForm {
  nombre: string;
  descripcion: string;
  tipo: string;
  contenido: string;
}

const ModelosComunicados = () => {
  const [modelos, setModelos] = useState<Modelo[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const [showModal, setShowModal] = useState(false);
  const [editingModelo, setEditingModelo] = useState<Modelo | null>(null);
  const [verifyDelete, setVerifyDelete] = useState<string | null>(null);

  const [formData, setFormData] = useState<ModeloForm>({
    nombre: '',
    descripcion: '',
    tipo: 'email',
    contenido: ''
  });

  const fetchModelos = async () => {
    try {
      const response = await api.get('/modelos-comunicados/');
      setModelos(response.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelos();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingModelo) {
        await api.put(`/modelos-comunicados/${editingModelo.id}`, formData);
      } else {
        await api.post('/modelos-comunicados/', formData);
      }
      setShowModal(false);
      resetForm();
      fetchModelos();
    } catch (error) {
      alert('Error al guardar modelo');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/modelos-comunicados/${id}`);
      setVerifyDelete(null);
      fetchModelos();
    } catch (error) {
      alert('Error al eliminar');
    }
  };

  const openEdit = (modelo: Modelo) => {
    setEditingModelo(modelo);
    setFormData({
      nombre: modelo.nombre,
      descripcion: modelo.descripcion,
      tipo: modelo.tipo,
      contenido: modelo.contenido
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setEditingModelo(null);
    setFormData({
      nombre: '',
      descripcion: '',
      tipo: 'email',
      contenido: ''
    });
  };

  const filtered = modelos.filter(m =>
    m.nombre.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Modelos de Comunicados</h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Crea plantillas reutilizables</p>
        </div>
        <button
          onClick={() => { resetForm(); setShowModal(true); }}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nuevo Modelo
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Buscar modelos..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <p className="text-center text-gray-500">Cargando...</p>
        ) : filtered.length === 0 ? (
          <p className="text-center text-gray-500">No hay modelos</p>
        ) : (
          filtered.map((modelo) => (
            <div key={modelo.id} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-3">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white">{modelo.nombre}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{modelo.descripcion}</p>
                <p className="text-xs text-gray-500 mt-1">Tipo: {modelo.tipo}</p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700/30 rounded p-3">
                <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3">{modelo.contenido}</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => openEdit(modelo)}
                  className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded hover:bg-blue-200 dark:hover:bg-blue-900/50"
                >
                  <Edit2 className="w-4 h-4" />
                  Editar
                </button>
                <button
                  onClick={() => setVerifyDelete(modelo.id)}
                  className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded hover:bg-red-200 dark:hover:bg-red-900/50"
                >
                  <Trash2 className="w-4 h-4" />
                  Eliminar
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editingModelo ? 'Editar Modelo' : 'Nuevo Modelo'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            required
            value={formData.nombre}
            onChange={(e) => setFormData({...formData, nombre: e.target.value})}
            placeholder="Nombre del modelo"
            className="w-full p-2 border rounded bg-white dark:bg-gray-700"
          />
          <input
            value={formData.descripcion}
            onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
            placeholder="Descripción (opcional)"
            className="w-full p-2 border rounded bg-white dark:bg-gray-700"
          />
          <select
            value={formData.tipo}
            onChange={(e) => setFormData({...formData, tipo: e.target.value})}
            className="w-full p-2 border rounded bg-white dark:bg-gray-700"
          >
            <option value="email">📧 Email</option>
            <option value="whatsapp">💬 WhatsApp</option>
            <option value="ambos">📧💬 Ambos</option>
          </select>
          <textarea
            required
            value={formData.contenido}
            onChange={(e) => setFormData({...formData, contenido: e.target.value})}
            placeholder="Contenido (usa {{nombre}}, {{email}}, {{whatsapp}})"
            className="w-full p-2 border rounded bg-white dark:bg-gray-700"
            rows={6}
          />
          <div className="flex gap-2">
            <button type="submit" className="flex-1 bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
              {editingModelo ? 'Actualizar' : 'Crear'} Modelo
            </button>
            <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-gray-300 dark:bg-gray-600 p-2 rounded">
              Cancelar
            </button>
          </div>
        </form>
      </Modal>

      {verifyDelete && (
        <Modal isOpen onClose={() => setVerifyDelete(null)} title="Confirmar eliminación">
          <p className="mb-4">¿Eliminar este modelo?</p>
          <div className="flex gap-2">
            <button onClick={() => handleDelete(verifyDelete)} className="flex-1 bg-red-600 text-white p-2 rounded hover:bg-red-700">
              Eliminar
            </button>
            <button onClick={() => setVerifyDelete(null)} className="flex-1 bg-gray-300 dark:bg-gray-600 p-2 rounded">
              Cancelar
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default ModelosComunicados;
