import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Contactos from './pages/Contactos';

// Placeholders for now
import Grupos from './pages/Grupos';
import Tareas from './pages/Tareas';
import Comunicados from './pages/Comunicados';
import ModelosComunicados from './pages/ModelosComunicados';

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
          <Route path="modelos-comunicados" element={<ModelosComunicados />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
