export interface Contacto {
    id: string;
    nombre: string;
    whatsapp?: string;
    email?: string;
    estado: "activo" | "inactivo";
    etiquetas: string[];
    notas?: string;
    fecha_agregado: string;
}

export interface Grupo {
    id: string;
    nombre: string;
    descripcion?: string;
    tipo: "email" | "whatsapp" | "ambos";
    estado: "activo" | "inactivo";
    fecha_creacion: string;
    cantidad_miembros?: number;  // Optional because it comes from a specific endpoint
}

export interface Tarea {
    id: string;
    titulo: string;
    descripcion?: string;
    fecha_creacion: string;
    fecha_termino?: string;
    prioridad: "baja" | "media" | "alta" | "urgente";
    estado: "pendiente" | "en_progreso" | "completada" | "cancelada";
    etiquetas: string[];
    urgencia?: "vencida" | "hoy" | "urgente" | "normal" | "sin_fecha";
    dias_restantes?: number;
}

export interface Comunicado {
    id: string;
    titulo: string;
    contenido: string;
    tipo: "email" | "whatsapp" | "ambos";
    estado: "borrador" | "programado" | "enviado" | "cancelado" | "error";
    fecha_programada?: string;
    hora_programada?: string;
    creado_en: string;
}
export interface ModeloComunicado {
    id: string;
    nombre: string;
    descripcion?: string;
    tipo: "email" | "whatsapp" | "ambos";
    contenido: string;
}
export interface ModeloComunicado {
    id: string;
    nombre: string;
    descripcion?: string;
    tipo: "email" | "whatsapp" | "ambos";
    contenido: string;
}