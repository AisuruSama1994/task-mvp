import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Contactos from './pages/Contactos';

// Placeholders for now
import Grupos from './pages/Grupos';
const Tareas = () => <div className="text-xl font-bold text-gray-800 dark:text-white">Tareas Page (En construcción)</div>;
const Comunicados = () => <div className="text-xl font-bold text-gray-800 dark:text-white">Comunicados Page (En construcción)</div>;

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="contactos" element={<Contactos />} />
          <Route path="grupos" element={<Grupos />} />
          <Route path="tareas" element={<Tareas />} />
          <Route path="comunicados" element={<Comunicados />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
