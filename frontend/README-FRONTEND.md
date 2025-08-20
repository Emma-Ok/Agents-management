# 🎨 Frontend - AI Agents Manager

Frontend moderno desarrollado con **Next.js 15** y **TypeScript** para gestionar agentes de inteligencia artificial y sus documentos.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
# Instalar dependencias base
npm install

# Instalar dependencias adicionales
./install-deps.sh
```

### 2. Configurar Variables de Entorno
```bash
# Crear archivo de configuración
cp .env.example .env.local

# Editar configuración si es necesario
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Ejecutar en Desarrollo
```bash
npm run dev
```

El frontend estará disponible en: **http://localhost:3000**

## 📁 Estructura del Proyecto

```
src/
├── app/                    # Next.js App Router
│   ├── dashboard/          # Página principal del dashboard
│   ├── agents/            # Gestión de agentes
│   ├── documents/         # Gestión de documentos
│   ├── layout.tsx         # Layout principal
│   └── page.tsx           # Página de inicio
├── components/            # Componentes reutilizables
│   ├── ui/               # Componentes base (Button, Card, etc.)
│   ├── agents/           # Componentes específicos de agentes
│   ├── documents/        # Componentes específicos de documentos
│   └── layout/           # Componentes de layout
├── hooks/                # Custom React hooks
│   ├── useAgents.ts      # Hook para gestión de agentes
│   └── useDocuments.ts   # Hook para gestión de documentos
├── services/             # Servicios de API
│   └── api.ts            # Cliente API para backend
├── types/                # Definiciones TypeScript
│   └── index.ts          # Tipos principales
├── lib/                  # Utilidades y configuraciones
│   └── utils.ts          # Funciones helper
└── utils/                # Funciones auxiliares
```

## 🎯 Funcionalidades Implementadas

### ✅ Dashboard Principal
- 📊 Estadísticas generales (agentes, documentos)
- 📋 Lista de agentes con tarjetas
- ➕ Creación rápida de agentes
- 🔍 Estado en tiempo real

### ✅ Gestión de Agentes
- 🤖 Crear agentes con nombre y prompt
- 📝 Formularios validados
- 🎨 Interfaz moderna y responsive
- ⚡ Estados de carga optimizados

### ✅ Conexión con Backend
- 🔌 API service completo
- 🔄 Hooks personalizados para estado
- ⚠️ Manejo de errores robusto
- 📡 Comunicación con FastAPI backend

## 🛠️ Tecnologías Utilizadas

- **⚛️ Next.js 15** - Framework React con App Router
- **🔷 TypeScript** - Tipado estático
- **🎨 Tailwind CSS** - Estilos utility-first
- **🪝 React Hooks** - Gestión de estado moderna
- **📡 Fetch API** - Comunicación HTTP
- **🎯 React Router** - Navegación

## 🔗 Integración con Backend

El frontend se conecta automáticamente con el backend FastAPI:

### Endpoints Utilizados:
- `GET /api/v1/agents` - Listar agentes
- `POST /api/v1/agents` - Crear agente
- `PUT /api/v1/agents/{id}` - Actualizar agente
- `DELETE /api/v1/agents/{id}` - Eliminar agente
- `POST /api/v1/documents/upload` - Subir documento
- `GET /health` - Estado del servidor

### Configuración:
```typescript
// Variables de entorno
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## 🎨 Componentes Principales

### AgentCard
Tarjeta para mostrar información de un agente:
- Nombre y prompt
- Contador de documentos
- Acciones rápidas
- Estado visual

### CreateAgentModal
Modal para crear nuevos agentes:
- Formulario validado
- Manejo de errores
- Estados de carga
- UX optimizada

### Dashboard
Página principal con:
- Estadísticas generales
- Grid de agentes
- Acciones principales
- Estado responsive

## 🚧 Próximas Funcionalidades

### 📅 En Desarrollo:
- 📤 Subida de documentos drag & drop
- 📋 Lista detallada de documentos
- 🔍 Vista previa de archivos
- ⚙️ Configuración de agentes
- 🔔 Notificaciones en tiempo real

### 🎯 Planificadas:
- 📊 Analytics avanzados
- 🎨 Temas personalizables
- 📱 PWA (Progressive Web App)
- 🔐 Autenticación de usuarios

## 🐛 Debugging

### Verificar Conexión Backend:
```bash
# Desde el navegador, abrir consola y ejecutar:
fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)
```

### Logs de Desarrollo:
```bash
# Ver logs en tiempo real
npm run dev

# Ver en browser devtools
F12 -> Console
```

### Estados de Error Comunes:
- ❌ Backend no responde: Verificar que `python main.py` esté ejecutándose
- ❌ CORS errors: Verificar configuración de CORS en backend
- ❌ API errors: Revisar URLs en variables de entorno

## 📱 Responsive Design

El frontend está optimizado para:
- 💻 **Desktop**: Grid completo con sidebar
- 📱 **Tablet**: Grid adaptativo
- 📱 **Mobile**: Stack vertical optimizado

---

¡Tu frontend está listo para conectarse con el backend! 🎉
