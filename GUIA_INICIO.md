# 🎯 Guía Rápida de Inicio - Sistema de Recordatorios

## ✅ Lo que ya está creado

### Backend Completo:
- ✅ Schema SQL con todas las tablas
- ✅ Modelos SQLAlchemy (Contacto, Grupo, Tarea, Comunicado, Logs)
- ✅ Schemas Pydantic con validaciones
- ✅ Providers:
  - ✅ Simulado (WhatsApp y Email) - **ACTIVO**
  - ✅ Gmail SMTP - **LISTO PARA USAR**
  - ✅ Twilio WhatsApp - Preparado para futuro
- ✅ Servicio de envío con reemplazo de variables
- ✅ Scheduler (APScheduler) para envíos programados
- ✅ API Contactos (CRUD completo)
- ✅ FastAPI app con CORS

### Pendiente:
- ⏳ API Grupos
- ⏳ API Tareas  
- ⏳ API Comunicados
- ⏳ Frontend React

---

## 🚀 Cómo Empezar AHORA

### Paso 1: Configurar PostgreSQL

```bash
# En WSL Ubuntu
sudo service postgresql start

# Conectar
psql -U postgres

# Crear base de datos
CREATE DATABASE recordatorios_db;

# Salir
\q

# Ejecutar schema
cd /home/maria/proyectos/task-mvp/backend
psql -U postgres -d recordatorios_db -f schema.sql
```

### Paso 2: Configurar Python

```bash
cd /home/maria/proyectos/task-mvp/backend

# Crear entorno virtual
python3 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Configurar .env

```bash
# Copiar ejemplo
cp .env.example .env

# Editar (usa nano o vim)
nano .env
```

**Configuración MÍNIMA para empezar (simulado):**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recordatorios_db
ENVIRONMENT=development
WHATSAPP_PROVIDER=simulated
EMAIL_PROVIDER=simulated
SCHEDULER_ENABLED=true
```

### Paso 4: Ejecutar Backend

```bash
# Desde /home/maria/proyectos/task-mvp/backend
cd app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Deberías ver:**
```
============================================================
🚀 Iniciando Sistema de Recordatorios
============================================================
Environment: development
WhatsApp Provider: simulated
Email Provider: simulated
Scheduler: Enabled
============================================================

🚀 Iniciando scheduler (intervalo: 60s)
✅ Scheduler iniciado correctamente
```

### Paso 5: Probar API

Abre en tu navegador:
- **Docs interactivos**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

---

## 📝 Probar Contactos API

### Crear contacto:

```bash
curl -X POST http://localhost:8000/api/contactos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "María Test",
    "email": "maria@test.com",
    "whatsapp": "+5491112345678",
    "etiquetas": ["test"]
  }'
```

### Listar contactos:

```bash
curl http://localhost:8000/api/contactos
```

### Buscar contactos:

```bash
curl "http://localhost:8000/api/contactos?search=maria"
```

---

## 🔧 Conectar tu Gmail (maria@escribanoschaco.com)

### 1. Crear App Password en Google

1. Ve a: https://myaccount.google.com/security
2. Busca "2-Step Verification" y actívalo si no está
3. Busca "App passwords"
4. Selecciona "Mail" y "Other (Custom name)"
5. Escribe "Sistema Recordatorios"
6. Copia la password de 16 caracteres que te da

### 2. Configurar .env

```env
EMAIL_PROVIDER=gmail
GMAIL_USER=maria@escribanoschaco.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
```

*Nota: Quita los espacios de la password*

### 3. Reiniciar servidor

```bash
# Ctrl+C para detener
# Volver a ejecutar:
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Ahora cuando envíes comunicados, se enviarán emails REALES desde tu cuenta.**

---

## 📋 Próximos Pasos

### Yo voy a crear ahora:

1. **API Grupos** - Para agrupar contactos
2. **API Tareas** - Para gestionar tareas
3. **API Comunicados** - Para crear y enviar mensajes
4. **Frontend React** - Interfaz visual

### Mientras tanto, tú puedes:

1. ✅ Configurar PostgreSQL
2. ✅ Instalar dependencias Python
3. ✅ Ejecutar el servidor
4. ✅ Probar la API de Contactos
5. ✅ (Opcional) Configurar Gmail

---

## 🐛 Problemas Comunes

### "ModuleNotFoundError: No module named 'app'"

```bash
# Asegúrate de estar en el directorio correcto:
cd /home/maria/proyectos/task-mvp/backend/app
python -m uvicorn main:app --reload
```

### "could not connect to server: Connection refused"

```bash
# PostgreSQL no está corriendo
sudo service postgresql start
```

### "relation 'contactos' does not exist"

```bash
# No ejecutaste el schema.sql
psql -U postgres -d recordatorios_db -f ../schema.sql
```

### "FATAL: password authentication failed"

Edita el `DATABASE_URL` en `.env` con tu password de PostgreSQL.

---

## 📞 Estado Actual

**Modo:** MVP con Simulado
- ✅ Contactos API funcionando
- ✅ Logs en consola (no envía real)
- ✅ Base de datos completa
- ✅ Listo para agregar más endpoints

**Siguiente:** Voy a crear las APIs de Grupos, Tareas y Comunicados ahora.

---

## 🎉 ¿Todo funcionando?

Si ves esto en http://localhost:8000:

```json
{
  "message": "Sistema de Recordatorios API",
  "version": "1.0.0",
  "status": "running",
  "providers": {
    "whatsapp": "simulated",
    "email": "simulated"
  }
}
```

**¡Perfecto! El backend está corriendo.** 🚀

Ahora puedo continuar creando el resto de las APIs.
