# 📚 Índice de Documentación - Proyecto Aegis Forge

**Versión:** 1.0.3 | **Última Actualización:** 2026-01-11

Este índice te guía a través de todos los documentos del proyecto, organizados por prioridad y relevancia.

---

## 🎯 Documentos Principales (LÉEME PRIMERO)

### 1. [PROJECT_STATUS.md](./PROJECT_STATUS.md) - 🆕 Estado Actual del Sistema
**Estado:** 🟢 Actualizado (2026-01-11)  
**Contenido:** Dashboard ejecutivo con estado operacional de todos los componentes, métricas, roadmap y troubleshooting.  
**Cuándo leer:** Para obtener una vista rápida y completa del estado actual del proyecto.

**Estado:** 🟢 Actualizado (2026-01-11)  
**Contenido:** Resumen de trabajo completado en esta sesión: Code Display UI, Vaccine #006, documentación actualizada.  
**Cuándo leer:** Para entender qué se hizo hoy y cuáles son los próximos pasos inmediatos.

### 2. [SPEC.MD](./SPEC.MD) - Especificación del Sistema
**Estado:** 📘 Documento Maestro  
**Contenido:** Arquitectura completa del sistema multi-agente, principios de diseño, stack tecnológico, y flujo de trabajo.  
**Cuándo leer:** Inicio del proyecto o cuando necesites entender la visión completa.

---

## 🧬 Memoria y Aprendizajes

### 2. [ai_learnings_v2.md](./ai_learnings_v2.md) - Bitácora de Vacunas
**Estado:** ✅ Activo (Vacunas #001-#007, Gemini 3 preview)  
**Contenido:**
- Historial de errores y soluciones (Vacunas #001-#007)
- Reglas de Oro por agente (incluye Retry+Cache+Rate Limit)
- Configuración de modelos Gemini 3 Preview
- Estado del proyecto actualizado

**Cuándo leer:** 
- Antes de implementar nuevos agentes
- Al debuggear errores recurrentes
- Para entender las lecciones aprendidas

### 3. [ai_learnings.md](./ai_learnings.md) - ⚠️ DEPRECADO
**Estado:** 🗄️ Archivo Histórico  
**Nota:** Reemplazado por `ai_learnings_v2.md`. Solo para referencia histórica.

---

## 📊 Reportes de Progreso

**Estado:** 🔄 En Progreso  
**Contenido:**
- Implementación del Agente 03 (El Constructor)
- Tareas completadas y pendientes
- Reglas de Oro para generación de código
- Integración con frontend (próxima fase)

**Cuándo leer:** Para entender el estado actual del Constructor y próximos pasos.

---

## 🩹 Vacunas Específicas

**Estado:** ✅ Completada  
**Contenido:**
- Análisis del error 404 (Model Not Found)
- Migración de gemini-1.5-* a gemini-2.0-*
- Creación de `model_config.py`
- Centralización de configuración

**Cuándo leer:** 
- Si hay errores de API de modelos
- Al agregar nuevos agentes
- Para entender la arquitectura de configuración

---

## 🗂️ Organización por Tema

### Arquitectura del Sistema
1. [SPEC.MD](./SPEC.MD) - Diseño completo
2. [model_config.py](./backend/model_config.py) - Configuración de modelos

### Implementación de Agentes
2. [agent_visionary.py](./backend/agent_visionary.py) - Agente 01
3. [agent_architect.py](./backend/agent_architect.py) - Agente 02
4. [agent_constructor.py](./backend/agent_constructor.py) - Agente 03

### Debugging y Lecciones
1. [ai_learnings_v2.md](./ai_learnings_v2.md) - Bitácora principal

---

## 📋 Checklist de Lectura para Nuevos Desarrolladores

- [ ] 1. Lee [PROJECT_STATUS.md](./PROJECT_STATUS.md) para el estado actual (10 min) ⭐ NUEVO
- [ ] 2. Lee [SPEC.MD](./SPEC.MD) completo (30 min)
- [ ] 3. Revisa [ai_learnings_v2.md](./ai_learnings_v2.md) - Sección "Reglas de Oro" (15 min)

**Tiempo total:** ~1 hora y 10 minutos

---

## 🚀 Estado Actual del Proyecto

| Componente | Estado | Documentación |
|:-----------|:-------|:--------------|
| Backend (FastAPI + LangGraph) | ✅ Funcionando | [SPEC.MD](./SPEC.MD) |
| Agente 01: Visionary | ✅ Implementado | [ai_learnings_v2.md](./ai_learnings_v2.md) |
| Agente 02: Architect | ✅ Implementado | [ai_learnings_v2.md](./ai_learnings_v2.md) |
| Frontend (Next.js) | ✅ Funcionando | [SPEC.MD](./SPEC.MD) |
| Vacunas #001-#007 | ✅ Aplicadas | [ai_learnings_v2.md](./ai_learnings_v2.md) |
| Agente 04: Auditor | ⏳ Por implementar | [SPEC.MD](./SPEC.MD) |
| Agente 05: Operador | ⏳ Por implementar | [SPEC.MD](./SPEC.MD) |
| Agente 06: Escriba | ⏳ Por implementar | [SPEC.MD](./SPEC.MD) |

---

## 🔍 Búsqueda Rápida

¿Necesitas información sobre...?

- **Errores de API/Fetch:** → [ai_learnings_v2.md](./ai_learnings_v2.md) - Vacunas #001, #003, #004
- **CORS issues:** → [ai_learnings_v2.md](./ai_learnings_v2.md) - Vacuna #004
- **Timeout management:** → [ai_learnings_v2.md](./ai_learnings_v2.md) - Vacuna #003
- **Arquitectura general:** → [SPEC.MD](./SPEC.MD)

---

## 📝 Convenciones de Documentación

### Estados de Documentos
- 📘 **Documento Maestro:** Especificación principal del sistema
- ✅ **Activo:** Documento actualizado y en uso
- 🔄 **En Progreso:** Documento que se actualiza frecuentemente
- 🗄️ **Histórico/Deprecado:** Solo para referencia, no usar
- ⏳ **Pendiente:** Característica no implementada aún

### Formato de Vacunas
Cada vacuna debe incluir:
1. **ID único** (ej: #005)
2. **Fecha** de identificación
3. **Agente afectado**
4. **Problema** (descripción del error)
5. **Causa raíz** (análisis técnico)
6. **Solución** (implementación concreta)
7. **Regla de Oro** (prevención futura)

---

## 🆘 ¿Cómo Contribuir a la Documentación?

1. **Encontraste un error nuevo:**
   - Agrégalo a [ai_learnings_v2.md](./ai_learnings_v2.md) con el próximo ID de vacuna
   - Incluye análisis de causa raíz
   - Define una "Regla de Oro" para prevenir reincidencia

2. **Completaste una tarea:**
   - Marca checkboxes como `[x]`
   - Agrega fecha de completado

3. **Implementaste un nuevo agente:**
   - Crea un archivo `AGENT_XX_PROGRESS.md` siguiendo la estructura del Agente 03
   - Agrega entrada en este índice
   - Documenta reglas específicas en [ai_learnings_v2.md](./ai_learnings_v2.md)

---

**Última revisión:** 2026-01-11  
**Mantenido por:** GitHub Copilot (Claude Sonnet 4.5)

## Backend Setup (Consolidado)

Requisitos:
- Python 3.12+
- GOOGLE_API_KEY en .env (raíz)

Instalación y ejecución:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Notas:
- Modelos centralizados en backend/model_config.py (Vacuna #005)
- CORS abierto en dev; restringir en prod (Vacuna #004)


## Frontend Setup (Consolidado)

Instalación y ejecución:

```bash
cd frontend
npm install
npm run dev
```

Notas:
- Usa NEXT_PUBLIC_API_URL para apuntar al backend
- No usar URLs hardcoded (Vacuna #004)

---

## 🧭 Guía Paso a Paso: Lanzamiento Local (Windows)

- **Pre-requisitos:** Python 3.12+, Node.js LTS (18/20+), PowerShell, clave `GOOGLE_API_KEY` válida.
- **Variables de entorno:**
  - Backend: crear el archivo en la raíz del proyecto [./.env](./.env) con:

```bash
# e:\Project Aegis Forge - Autonomous Vibe Coding SaaS\.env
GOOGLE_API_KEY=tu_api_key_de_gemini
```

  - Frontend: verificar [frontend/.env.local](./frontend/.env.local) contenga:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- **Instalar y arrancar Backend:**

```powershell
& ".venv\Scripts\Activate.ps1"
pip install -r backend\requirements.txt
# ⚠️ IMPORTANTE: NO ejecutar python backend/main.py (causará ImportError)
# ✅ Usar uvicorn para ejecución modular:
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

- **Probar Backend (salud):**

```powershell
Invoke-RestMethod -Uri http://localhost:8000/ | ConvertTo-Json -Depth 4
```

Debe responder: `{ "status": "ok" }`.

- **Instalar y arrancar Frontend:**

```powershell
cd frontend
npm install
npm run dev
```

- **Abrir la app:** Navega a `http://localhost:3000`.

- **Prueba E2E (sugerida):** Ingresa un prompt como:
  "Crea una landing page para una app de fitness con Next.js y TailwindCSS, incluye un hero con CTA y grid de características".
  - Espera ver: Especificación → Plan → Código generado → Panel de archivos.

- **Troubleshooting rápido:**
  - **Backend offline:** verifica que `uvicorn` esté corriendo y que [./.env](./.env) tenga `GOOGLE_API_KEY`.
  - **CORS/Fetch:** en dev `allow_origins=["*"]` ya está activo; asegúrate de que `NEXT_PUBLIC_API_URL` tenga protocolo (`http://`).
  - **429 Rate Limit (Gemini):** espera unos segundos o reduce frecuencia; el backend aplica `slowapi` + caché.
  - **Modelos:** puedes overridear por entorno: `GEMINI_FLASH_MODEL` / `GEMINI_PRO_MODEL` (ver [backend/model_config.py](./backend/model_config.py)).
