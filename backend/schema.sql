-- ============================================
-- Sistema de Recordatorios - Database Schema
-- PostgreSQL 14+
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- CONTACTOS
-- ============================================

CREATE TABLE contactos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255) NOT NULL,
    whatsapp VARCHAR(20),
    email VARCHAR(255),
    fecha_agregado TIMESTAMPTZ DEFAULT NOW(),
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    etiquetas TEXT[] DEFAULT '{}',
    notas TEXT,
    CONSTRAINT valid_email CHECK (email IS NULL OR email ~ '^[^@]+@[^@]+\.[^@]+$'),
    CONSTRAINT valid_whatsapp CHECK (whatsapp IS NULL OR whatsapp ~ '^\+[0-9]{10,15}$')
);

COMMENT ON TABLE contactos IS 'Contactos individuales del sistema';
COMMENT ON COLUMN contactos.whatsapp IS 'Formato: +5491112345678 (código país + número)';
COMMENT ON COLUMN contactos.etiquetas IS 'Array de etiquetas: cliente, proveedor, etc.';

CREATE INDEX idx_contactos_estado ON contactos(estado);
CREATE INDEX idx_contactos_nombre ON contactos(nombre);
CREATE INDEX idx_contactos_email ON contactos(email);

-- ============================================
-- GRUPOS
-- ============================================

CREATE TABLE grupos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('email', 'whatsapp', 'ambos')),
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo'))
);

COMMENT ON TABLE grupos IS 'Grupos de comunicación';
COMMENT ON COLUMN grupos.tipo IS 'Tipo de comunicación: email, whatsapp, ambos';

CREATE INDEX idx_grupos_estado ON grupos(estado);
CREATE INDEX idx_grupos_tipo ON grupos(tipo);

-- ============================================
-- GRUPO_MIEMBROS (Relación muchos a muchos)
-- ============================================

CREATE TABLE grupo_miembros (
    grupo_id UUID REFERENCES grupos(id) ON DELETE CASCADE,
    contacto_id UUID REFERENCES contactos(id) ON DELETE CASCADE,
    fecha_agregado TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (grupo_id, contacto_id)
);

COMMENT ON TABLE grupo_miembros IS 'Relación muchos a muchos entre grupos y contactos';

CREATE INDEX idx_grupo_miembros_grupo ON grupo_miembros(grupo_id);
CREATE INDEX idx_grupo_miembros_contacto ON grupo_miembros(contacto_id);

-- ============================================
-- TAREAS
-- ============================================

CREATE TABLE tareas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_creacion DATE NOT NULL,
    hora_creacion TIME,
    fecha_termino DATE,
    hora_termino TIME,
    prioridad VARCHAR(20) DEFAULT 'media' CHECK (prioridad IN ('baja', 'media', 'alta', 'urgente')),
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_progreso', 'completada', 'cancelada')),
    etiquetas TEXT[] DEFAULT '{}',
    fecha_creacion_record TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_completacion TIMESTAMPTZ
);

COMMENT ON TABLE tareas IS 'Tareas del sistema';
COMMENT ON COLUMN tareas.fecha_creacion IS 'Fecha de creación de la tarea (no del registro)';
COMMENT ON COLUMN tareas.fecha_creacion_record IS 'Timestamp de cuando se creó el registro en BD';

CREATE INDEX idx_tareas_estado ON tareas(estado);
CREATE INDEX idx_tareas_prioridad ON tareas(prioridad);
CREATE INDEX idx_tareas_fecha_termino ON tareas(fecha_termino);
CREATE INDEX idx_tareas_fecha_creacion ON tareas(fecha_creacion);

-- ============================================
-- TAREA_ADJUNTOS
-- ============================================

CREATE TABLE tarea_adjuntos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tarea_id UUID REFERENCES tareas(id) ON DELETE CASCADE,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_agregado TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE tarea_adjuntos IS 'Archivos adjuntos a tareas';

CREATE INDEX idx_tarea_adjuntos_tarea ON tarea_adjuntos(tarea_id);

-- ============================================
-- COMUNICADOS
-- ============================================

CREATE TABLE comunicados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('whatsapp', 'email', 'ambos')),
    contenido TEXT NOT NULL,
    estado VARCHAR(30) DEFAULT 'borrador' CHECK (estado IN ('borrador', 'programado', 'enviado', 'parcialmente_enviado', 'error')),
    fecha_programada DATE,
    hora_programada TIME,
    fecha_envio_real TIMESTAMPTZ,
    variables_disponibles TEXT[] DEFAULT ARRAY['{{nombre}}', '{{email}}', '{{whatsapp}}'],
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    creado_por VARCHAR(255)
);

COMMENT ON TABLE comunicados IS 'Comunicados para enviar por WhatsApp/Email';
COMMENT ON COLUMN comunicados.variables_disponibles IS 'Variables que se pueden usar en el contenido';

CREATE INDEX idx_comunicados_estado ON comunicados(estado);
CREATE INDEX idx_comunicados_fecha_programada ON comunicados(fecha_programada, hora_programada);
CREATE INDEX idx_comunicados_tipo ON comunicados(tipo);

-- ============================================
-- COMUNICADO_ADJUNTOS
-- ============================================

CREATE TABLE comunicado_adjuntos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comunicado_id UUID REFERENCES comunicados(id) ON DELETE CASCADE,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_agregado TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE comunicado_adjuntos IS 'Archivos adjuntos a comunicados';

CREATE INDEX idx_comunicado_adjuntos_comunicado ON comunicado_adjuntos(comunicado_id);

-- ============================================
-- COMUNICADO_DESTINATARIOS
-- ============================================

CREATE TABLE comunicado_destinatarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comunicado_id UUID REFERENCES comunicados(id) ON DELETE CASCADE,
    contacto_id UUID REFERENCES contactos(id),
    grupo_id UUID REFERENCES grupos(id),
    estado_envio VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_envio IN ('pendiente', 'enviado', 'error', 'reintentos')),
    intentos_fallidos INT DEFAULT 0,
    error_mensaje TEXT,
    fecha_envio TIMESTAMPTZ,
    CHECK (contacto_id IS NOT NULL OR grupo_id IS NOT NULL)
);

COMMENT ON TABLE comunicado_destinatarios IS 'Destinatarios de cada comunicado (contactos o grupos)';
COMMENT ON COLUMN comunicado_destinatarios.intentos_fallidos IS 'Contador de intentos fallidos (máximo 3)';

CREATE INDEX idx_comunicado_destinatarios_comunicado ON comunicado_destinatarios(comunicado_id);
CREATE INDEX idx_comunicado_destinatarios_contacto ON comunicado_destinatarios(contacto_id);
CREATE INDEX idx_comunicado_destinatarios_grupo ON comunicado_destinatarios(grupo_id);
CREATE INDEX idx_comunicado_destinatarios_estado ON comunicado_destinatarios(estado_envio);

-- ============================================
-- COMUNICADOS_LOG
-- ============================================

CREATE TABLE comunicados_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comunicado_id UUID REFERENCES comunicados(id),
    contacto_id UUID REFERENCES contactos(id),
    tipo_comunicado VARCHAR(20) CHECK (tipo_comunicado IN ('whatsapp', 'email')),
    contenido_enviado TEXT,
    fecha_envio TIMESTAMPTZ DEFAULT NOW(),
    resultado VARCHAR(20) CHECK (resultado IN ('exitoso', 'fallido')),
    motivo_error TEXT,
    intento INT DEFAULT 1
);

COMMENT ON TABLE comunicados_log IS 'Log completo de todos los envíos realizados';
COMMENT ON COLUMN comunicados_log.contenido_enviado IS 'Mensaje final con variables reemplazadas';

CREATE INDEX idx_comunicados_log_comunicado ON comunicados_log(comunicado_id);
CREATE INDEX idx_comunicados_log_contacto ON comunicados_log(contacto_id);
CREATE INDEX idx_comunicados_log_fecha ON comunicados_log(fecha_envio);
CREATE INDEX idx_comunicados_log_resultado ON comunicados_log(resultado);

-- ============================================
-- TAREAS_LOG
-- ============================================

CREATE TABLE tareas_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tarea_id UUID REFERENCES tareas(id),
    accion VARCHAR(50) CHECK (accion IN ('creada', 'actualizada', 'completada', 'cancelada', 'estado_cambio')),
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    fecha_cambio TIMESTAMPTZ DEFAULT NOW(),
    usuario VARCHAR(255)
);

COMMENT ON TABLE tareas_log IS 'Historial de cambios en tareas';
COMMENT ON COLUMN tareas_log.datos_anteriores IS 'Estado anterior de la tarea en formato JSON';
COMMENT ON COLUMN tareas_log.datos_nuevos IS 'Estado nuevo de la tarea en formato JSON';

CREATE INDEX idx_tareas_log_tarea ON tareas_log(tarea_id);
CREATE INDEX idx_tareas_log_fecha ON tareas_log(fecha_cambio);
CREATE INDEX idx_tareas_log_accion ON tareas_log(accion);

-- ============================================
-- TRIGGERS
-- ============================================

-- Función para actualizar fecha_actualizacion automáticamente
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para tareas
CREATE TRIGGER update_tarea_timestamp
BEFORE UPDATE ON tareas
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Contactos con cantidad de grupos
CREATE VIEW v_contactos_con_grupos AS
SELECT 
    c.*,
    COUNT(gm.grupo_id) as cantidad_grupos
FROM contactos c
LEFT JOIN grupo_miembros gm ON c.id = gm.contacto_id
GROUP BY c.id;

COMMENT ON VIEW v_contactos_con_grupos IS 'Contactos con cantidad de grupos a los que pertenecen';

-- Vista: Grupos con cantidad de miembros
CREATE VIEW v_grupos_con_miembros AS
SELECT 
    g.*,
    COUNT(gm.contacto_id) as cantidad_miembros
FROM grupos g
LEFT JOIN grupo_miembros gm ON g.id = gm.grupo_id
GROUP BY g.id;

COMMENT ON VIEW v_grupos_con_miembros IS 'Grupos con cantidad de miembros';

-- Vista: Tareas con días restantes
CREATE VIEW v_tareas_con_urgencia AS
SELECT 
    t.*,
    CASE 
        WHEN t.fecha_termino IS NULL THEN NULL
        ELSE t.fecha_termino - CURRENT_DATE
    END as dias_restantes,
    CASE 
        WHEN t.fecha_termino IS NULL THEN 'sin_fecha'
        WHEN t.fecha_termino < CURRENT_DATE THEN 'vencida'
        WHEN t.fecha_termino = CURRENT_DATE THEN 'hoy'
        WHEN t.fecha_termino <= CURRENT_DATE + INTERVAL '3 days' THEN 'urgente'
        ELSE 'normal'
    END as urgencia
FROM tareas t;

COMMENT ON VIEW v_tareas_con_urgencia IS 'Tareas con cálculo de días restantes y nivel de urgencia';

-- Vista: Estadísticas de comunicados
CREATE VIEW v_estadisticas_comunicados AS
SELECT 
    c.id,
    c.titulo,
    c.tipo,
    c.estado,
    COUNT(cd.id) as total_destinatarios,
    COUNT(CASE WHEN cd.estado_envio = 'enviado' THEN 1 END) as enviados,
    COUNT(CASE WHEN cd.estado_envio = 'error' THEN 1 END) as errores,
    COUNT(CASE WHEN cd.estado_envio = 'pendiente' THEN 1 END) as pendientes
FROM comunicados c
LEFT JOIN comunicado_destinatarios cd ON c.id = cd.comunicado_id
GROUP BY c.id;

COMMENT ON VIEW v_estadisticas_comunicados IS 'Estadísticas de envío por comunicado';

-- ============================================
-- DATOS DE EJEMPLO (Opcional - para testing)
-- ============================================

-- Insertar contactos de ejemplo
INSERT INTO contactos (nombre, email, whatsapp, etiquetas) VALUES
('Juan Pérez', 'juan@example.com', '+5491112345678', ARRAY['cliente', 'vip']),
('María López', 'maria@example.com', '+5491187654321', ARRAY['proveedor']),
('Carlos Ruiz', 'carlos@example.com', '+5491123456789', ARRAY['cliente']);

-- Insertar grupo de ejemplo
INSERT INTO grupos (nombre, descripcion, tipo) VALUES
('Clientes VIP', 'Clientes prioritarios', 'ambos'),
('Proveedores', 'Proveedores habituales', 'email');

-- Insertar tarea de ejemplo
INSERT INTO tareas (titulo, descripcion, fecha_creacion, fecha_termino, prioridad, estado) VALUES
('Revisar contratos', 'Revisar contratos pendientes de firma', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', 'alta', 'pendiente');

COMMENT ON DATABASE CURRENT_DATABASE() IS 'Sistema de Recordatorios - WhatsApp y Email';
