# Sistema de Recordatorios - WhatsApp y Email

Sistema completo de gestión de tareas y envío de recordatorios por WhatsApp y Email.

## 🚀 Stack Tecnológico

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React + TypeScript + Tailwind CSS (próximamente)
- **Scheduler**: APScheduler
- **Providers**: Simulado (MVP) → Gmail + Twilio (Producción)

## 📋 Requisitos

- Python 3.10+
- PostgreSQL 14+
- Node.js 18+ (para frontend)

## 🛠️ Instalación

### 1. Clonar y configurar backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/WSL:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar PostgreSQL

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE recordatorios_db;

# Salir
\q

# Ejecutar schema
psql -U postgres -d recordatorios_db -f schema.sql
```

### 3. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
nano .env
```

**Configuración mínima para MVP (simulado):**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recordatorios_db
WHATSAPP_PROVIDER=simulated
EMAIL_PROVIDER=simulated
```

**Para conectar tu Gmail (maria@escribanoschaco.com):**

1. Ve a https://myaccount.google.com/security
2. Activa "2-Step Verification"
3. Ve a "App passwords"
4. Genera una nueva password para "Mail"
5. Copia la password generada

Luego en `.env`:
```env
EMAIL_PROVIDER=gmail
GMAIL_USER=maria@escribanoschaco.com
GMAIL_APP_PASSWORD=tu_app_password_de_16_caracteres
```

### 4. Ejecutar backend

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará en: http://localhost:8000

Documentación API: http://localhost:8000/docs

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py                    # FastAPI app principal
│   ├── config.py                  # Configuración
│   ├── database.py                # SQLAlchemy setup
│   ├── models/                    # Modelos de BD
│   │   ├── contacto.py
│   │   ├── tarea.py
│   │   ├── comunicado.py
│   │   └── log.py
│   ├── schemas/                   # Pydantic schemas
│   │   ├── contacto.py
│   │   ├── tarea.py
│   │   └── comunicado.py
│   ├── routes/                    # Endpoints API
│   │   ├── contactos.py
│   │   ├── grupos.py
│   │   ├── tareas.py
│   │   └── comunicados.py
│   ├── services/                  # Lógica de negocio
│   │   ├── base_provider.py      # Interfaces abstractas
│   │   ├── simulated_provider.py # Providers simulados
│   │   ├── gmail_provider.py     # Gmail SMTP
│   │   ├── twilio_provider.py    # Twilio WhatsApp
│   │   └── envio_service.py      # Servicio de envío
│   └── tasks/                     # Tareas programadas
│       └── scheduler.py           # APScheduler
├── schema.sql                     # Schema de BD
├── requirements.txt
└── .env.example
```

## 🔄 Flujo de Trabajo

### 1. Crear Contactos

```bash
POST /api/contactos
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "whatsapp": "+5491112345678",
  "etiquetas": ["cliente", "vip"]
}
```

### 2. Crear Grupos

```bash
POST /api/grupos
{
  "nombre": "Clientes VIP",
  "tipo": "ambos",
  "descripcion": "Clientes prioritarios"
}

# Agregar miembros
POST /api/grupos/{grupo_id}/miembros/{contacto_id}
```

### 3. Crear Tareas

```bash
POST /api/tareas
{
  "titulo": "Revisar contratos",
  "descripcion": "Contratos pendientes de firma",
  "fecha_creacion": "2026-02-03",
  "fecha_termino": "2026-02-06",
  "prioridad": "alta"
}
```

### 4. Crear y Enviar Comunicado

```bash
# Crear comunicado
POST /api/comunicados
{
  "titulo": "Recordatorio de reunión",
  "tipo": "ambos",
  "contenido": "Hola {{nombre}}, te recordamos la reunión de mañana.",
  "destinatarios_contactos": ["uuid-contacto-1"],
  "destinatarios_grupos": ["uuid-grupo-1"]
}

# Vista previa
POST /api/comunicados/{id}/vista-previa

# Programar envío
POST /api/comunicados/{id}/enviar
{
  "fecha_programada": "2026-02-04",
  "hora_programada": "09:00:00"
}
```

## 🎯 Providers Disponibles

### Simulado (MVP - Actual)
- ✅ Sin costos
- ✅ Sin configuración
- ✅ Logs completos
- ❌ No envía mensajes reales

### Gmail (Email Real)
- ✅ Gratis
- ✅ Usa tu email: maria@escribanoschaco.com
- ✅ SMTP nativo
- ⚙️ Requiere App Password

### Twilio (WhatsApp Real - Futuro)
- ✅ Oficial y confiable
- ✅ Escalable
- 💰 ~$0.005 por mensaje
- ⚙️ Requiere cuenta Twilio

## 🔧 Cambiar de Simulado a Real

### Para activar Gmail:

1. Configura App Password (ver arriba)
2. Edita `.env`:
   ```env
   EMAIL_PROVIDER=gmail
   GMAIL_USER=maria@escribanoschaco.com
   GMAIL_APP_PASSWORD=tu_password_aqui
   ```
3. Reinicia el servidor
4. ¡Listo! Ahora envía emails reales

### Para activar Twilio (futuro):

1. Crea cuenta en https://www.twilio.com
2. Obtén credenciales
3. Edita `.env`:
   ```env
   WHATSAPP_PROVIDER=twilio
   TWILIO_ACCOUNT_SID=tu_sid
   TWILIO_AUTH_TOKEN=tu_token
   TWILIO_WHATSAPP_NUMBER=+14155238886
   ```
4. Descomenta código en `twilio_provider.py`
5. `pip install twilio`
6. Reinicia el servidor

## 📊 Variables Disponibles en Comunicados

- `{{nombre}}` - Nombre del contacto
- `{{email}}` - Email del contacto
- `{{whatsapp}}` - WhatsApp del contacto

Ejemplo:
```
Hola {{nombre}}, 

Te escribimos al email {{email}} para recordarte...
```

Se reemplaza automáticamente por:
```
Hola Juan Pérez,

Te escribimos al email juan@example.com para recordarte...
```

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL
```bash
# Verifica que PostgreSQL esté corriendo
sudo service postgresql status

# Inicia PostgreSQL
sudo service postgresql start
```

### Error de autenticación Gmail
- Verifica que usaste App Password, NO tu contraseña normal
- Verifica que 2-Step Verification esté activado
- Genera una nueva App Password si es necesario

### Scheduler no funciona
- Verifica `SCHEDULER_ENABLED=true` en `.env`
- Revisa logs en consola
- Verifica que la fecha/hora programada sea futura

## 📝 Próximos Pasos

1. ✅ Backend completo con simulado
2. ⏳ Crear endpoints (próximo)
3. ⏳ Frontend React
4. ⏳ Conectar Gmail real
5. ⏳ Agregar Twilio (opcional)

## 🤝 Soporte

Para cualquier duda o problema, revisa:
- Documentación API: http://localhost:8000/docs
- Logs del servidor en consola
- Archivo `.env` configurado correctamente
