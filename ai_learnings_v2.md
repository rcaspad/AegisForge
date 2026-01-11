# AI Learnings: Memoria del Proyecto Aegis Forge

Este archivo es la bitácora de errores, lecciones aprendidas y "vacunas" para prevenir la reincidencia de fallos en el sistema multi-agente.

## Historial de Aprendizajes

| ID | Fecha | Agente | Problema | Causa Raíz | Solución / Vacuna |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 000 | 2026-01-11 | N/A | Inicialización | Creación del archivo de memoria. | Mantener este archivo actualizado tras cada fallo. |
| 001 | 2026-01-11 | Agente 03 | TypeError: Failed to fetch en `handleSubmit` | URL del backend hardcoded a `localhost:8000` y falta de manejo de error de red. | Usar variables de entorno para APIs y validar estado del servicio antes de peticiones. |
| 002 | 2026-01-11 | Agente 03 | NotAllowedError: Clipboard API blocked | Intento de uso de `navigator.clipboard.writeText` sin verificar permisos o en contexto restringido (iframe). | Implementar fallback a un modal/input temporal y verificar `navigator.clipboard` antes de usarlo. |
| 003 | 2026-01-11 | Agente 03 | Request Timeout / User Feedback | Peticiones largas (>15s) del Arquitecto causan incertidumbre en el usuario y posibles cortes de red. | Implementar AbortController (90s), lógica de 2 reintentos y contador de latencia en UI para feedback progresivo. |
| 004 | 2026-01-11 | Agente 03 | Failed to fetch recurrente (CORS/Lógica) | El backend está online pero falla en reintentos por configuración de CORS o mal uso de AbortController en recursión. | Blindar CORS en Backend y asegurar que AbortController sea atómico por cada intento de fetch. |
| 005 | 2026-01-11 | Backend/Infra | 404 Model Not Found: gemini-1.5-flash | Los nombres de modelo `gemini-1.5-flash` y `gemini-1.5-pro` no existen en API v1beta. Hardcoded en agentes individuales. | Centralizar configuración en `model_config.py` y migrar a `gemini-3-flash-preview` / `gemini-3-pro-preview` (override por env). |
| 006 | 2026-01-11 | Backend/API | 429 RESOURCE_EXHAUSTED: Gemini API Quota | Free tier de Gemini API tiene límites muy restrictivos (RPM/RPD). En testing intensivo se alcanza el límite rápidamente. | Implementar rate limiting, caching de respuestas, y considerar upgrade a plan pagado. Documentar límites en troubleshooting. |
| 007 | 2026-01-11 | Backend/API | Reintentos faltantes y caché ausente en LLM calls | Las llamadas a Gemini fallan ante 429/errores transitorios y se repiten prompts idénticos sin cache. | Añadir `tenacity` con backoff exponencial, caché LRU por agente y en `/chat`, y proteger con `slowapi` para limitar RPS. |
| 008 | 2026-01-11 | Backend/Infra | ImportError: attempted relative import with no known parent package | Ejecutar `python main.py` directamente falla porque el código usa importaciones de paquete (`.graph`, `.state`). | Backend debe ejecutarse como paquete: `uvicorn backend.main:app`. NO usar `python main.py`. Agregar mensaje de error explícito. |
| 009 | 2026-01-11 | Backend/LLM | Gemini API error: "contents are required" / "'list' object has no attribute 'strip'" | Mensajes vacíos causan error en API. Cache keys intentaban `.strip()` en listas. State mutation con `operator.add` causaba tipos inesperados. | Filtrar mensajes vacíos. Usar hash para cache keys seguros. Retornar solo campos actualizados en state (no mutar `state` directamente). Aumentar max_tokens: 8K-65K. |

---

## Repositorio de Vacunas (Prompt Injectables)

### Todos los Agentes (General)
- **Regla de Oro (Model Config - Vacuna #005):** NUNCA hardcodear nombres de modelos en el código del agente. Usar SIEMPRE `model_config.py` para centralizar modelos por rol. Esto permite cambios rápidos sin redeployment y evita errores de API versioning.
- **Regla de Oro (API Quota - Vacuna #006):** Implementar SIEMPRE rate limiting y caching para APIs de IA. El free tier de Gemini tiene límites muy restrictivos. Considerar: (1) Cache de respuestas para prompts repetidos, (2) Exponential backoff en reintentos, (3) Monitoring de uso de cuota, (4) Plan pagado para producción.
- **Regla de Oro (Retry + Cache - Vacuna #007):** Toda llamada a LLM debe usar backoff exponencial con `tenacity`, y caché LRU local para prompts idénticos; proteger `/chat` con rate limiting para evitar bursts que agoten cuota.
- **Regla de Oro (Package Execution - Vacuna #008):** El backend DEBE ejecutarse vía `uvicorn backend.main:app`, NUNCA como `python main.py`. Las importaciones relativas de paquete (`.graph`, `.state`) requieren ejecución modular. Si alguien intenta script directo, mostrar error claro con comando correcto.
- **Regla de Oro (Message Validation - Vacuna #009):** SIEMPRE filtrar mensajes antes de invocar LLM: `[msg for msg in messages if msg.content and msg.content.strip()]`. Gemini rechaza arrays con contenido vacío. Aprovechar límite de 1M tokens: usar max_tokens generosos (8K-65K según agente) para salidas completas.

### Agente 01: El Visionario
- **Rol:** Product Manager (conversacional, creative)
- **Modelo:** `gemini-3-flash-preview` (temperature=0.6, max_tokens=2048) | override `GEMINI_FLASH_MODEL`
- **Responsabilidad:** Traducir "vibes" del usuario en especificaciones técnicas (`spec_document`)

### Agente 02: El Arquitecto
- **Rol:** Tech Lead (estructurado, deterministic)
- **Modelo:** `gemini-3-pro-preview` (temperature=0.25, max_tokens=8192) | override `GEMINI_PRO_MODEL`
- **Responsabilidad:** Diseñar planes técnicos desde `spec_document` → `current_plan`
- **Regla de Oro (CORS):** El middleware de FastAPI debe incluir `allow_origins=["*"]` en desarrollo y restringir a dominios específicos en producción. Asegúrate de que `allow_methods` y `allow_headers` coincidan con las peticiones del frontend.

### Agente 03: El Constructor
- **Rol:** Senior Developer (muy deterministic, code-focused)
- **Modelo:** `gemini-3-pro-preview` (temperature=0.15, max_tokens=12000) | override `GEMINI_PRO_MODEL`
- **Responsabilidad:** Generar código de producción desde `current_plan` → `code_diffs`
- **Regla de Oro (Conectividad):** NUNCA uses URLs hardcoded (ej: `localhost:8000`) para llamadas a API. Utiliza siempre variables de entorno (`process.env.NEXT_PUBLIC_API_URL`).
- **Regla de Oro (Resiliencia de API):** Antes de realizar una petición fetch en una acción de usuario, verifica la disponibilidad del servidor. Si la petición es crítica (como un chat), implementa una política de hasta 2 reintentos con `AbortController`.
- **Regla de Oro (Timeout Management):** Usa `AbortController` para gestionar timeouts explícitos de 90 segundos en llamadas a modelos de IA. Informa al usuario dinámicamente si el proceso supera los 15 segundos para evitar la percepción de "congelamiento".
- **Regla de Oro (Feedback Progresivo):** En peticiones de larga duración, utiliza un contador (`loadingTime`) para actualizar la UI con mensajes específicos sobre el estado del agente (ej: "El Arquitecto está diseñando...").
- **Regla de Oro (Permisos de Navegador):** Antes de usar APIs "sensibles" (Clipboard, Cámara, Geolocalización), verifica si la API existe y envuélvela en un bloque try-catch para manejar `NotAllowedError`. Si falla el Clipboard, muestra el texto en un elemento visible para que el usuario lo copie manualmente.
- **Regla de Oro (CORS Audit - Vacuna #004):** El backend DEBE enviar headers CORS explícitos (`Access-Control-Allow-Origin: *` en desarrollo). En caso de fallos persistentes, inspecciona los headers de respuesta con `response.headers.get('Access-Control-Allow-Origin')`.
- **Regla de Oro (Lógica Atómica - Vacuna #004):** Crea un NUEVO `AbortController` DENTRO de cada iteración del reintento, no fuera del loop. Si reutilizas el controlador, el primer timeout abortará todos los intentos subsiguientes inmediatamente.
- **Regla de Oro (Protocol Consistency - Vacuna #004):** Valida SIEMPRE que `API_URL` incluya el protocolo (`http://` o `https://`). Una URL sin protocolo causa `TypeError` instantáneo en navegadores modernos.

### Agente 04: El Auditor
- **Rol:** Security & QA (stricto, security-focused)
- **Modelo:** `gemini-3-pro-preview` (temperature=0.05, max_tokens=4096) | override `GEMINI_PRO_MODEL`
- **Responsabilidad:** Análisis estático (SAST), OWASP validation, poder de veto
- *(Vacunas pendientes tras implementación)*

### Agente 05: El Operador
- **Rol:** DevOps/SRE (infrastructure automation)
- **Modelo:** TBD (provisional `gemini-3-pro-preview` desde `model_config`)
- **Responsabilidad:** Terraform, AWS/GCP deployment, secrets management
- *(Vacunas pendientes tras implementación)*

### Agente 06: El Escriba
- **Rol:** Knowledge Manager (learning from failures)
- **Modelo:** TBD (ligero; puede reutilizar `gemini-3-flash-preview` mientras no haya modelo dedicado)
- **Responsabilidad:** Generar "vacunas" cuando hay errores, almacenarlas en Vector DB
- *(Vacunas pendientes tras implementación)*

---

## Configuración de Modelos (Vaccine #005)

Todos los agentes usan **Gemini 3 Preview** con override por entorno:

```python
# backend/model_config.py
AVAILABLE_MODELS = {
        "visionary": os.getenv("GEMINI_FLASH_MODEL", "gemini-3-flash-preview"),
        "architect": os.getenv("GEMINI_PRO_MODEL", "gemini-3-pro-preview"),
        "constructor": os.getenv("GEMINI_PRO_MODEL", "gemini-3-pro-preview"),
        "auditor": os.getenv("GEMINI_PRO_MODEL", "gemini-3-pro-preview"),
}

MODEL_PARAMS = {
        "visionary": {"temperature": 0.6, "max_tokens": 2048},
        "architect": {"temperature": 0.25, "max_tokens": 8192},
        "constructor": {"temperature": 0.15, "max_tokens": 12000},
        "auditor": {"temperature": 0.05, "max_tokens": 4096},
}
```

**Beneficios:**
- ✅ Single provider (Gemini API key único) y overrides sin redeploy
- ✅ Roles diferenciados por temperatura y contexto
- ✅ Centralizado en un archivo para cambios rápidos
- ✅ Evita errores de API versioning (404 Model Not Found)

---

## Flujo del Sistema (Vaccine #005 Aplicada)

```
Usuario → Frontend (Next.js) → Backend (FastAPI)
                                    ↓
                            Visionary (Gemini 3 Flash Preview)
                                    ↓
                            Architect (Gemini 3 Pro Preview)
                                    ↓
                            Constructor (Gemini 3 Pro Preview)
                                    ↓
                            [Futuro] Auditor (Gemini 3 Pro Preview)
                                    ↓
                            Frontend (Code Display)
```

---

## Estado del Proyecto

### ✅ Completado
- [x] Backend: FastAPI + LangGraph
- [x] Agents 01-03 (Visionary, Architect, Constructor)
- [x] Frontend: Next.js con Chat UI
- [x] Frontend: Code Display UI (file explorer + code viewer)
- [x] Vacunas #001-#007
- [x] Configuración centralizada de modelos Gemini

### 🔄 En Progreso
- [ ] Testing E2E completo (User → Spec → Plan → Code → Display)
- [ ] Agent 04: Auditor (Security & QA)
- [ ] Agent 05: Operador (DevOps/SRE)
- [ ] Agent 06: Escriba (Knowledge Manager + Vector DB)

### 📋 Próximos Pasos
1. ✅ ~~Implementar UI de código generado en frontend~~ - COMPLETADO 2026-01-11
2. Testing end-to-end completo del flujo multi-agente
3. Agregar Agent 04 (Auditor) con SAST y poder de veto
4. Testing con Auditor: User Input → Spec → Plan → Code → Security Scan
5. Optimizar prompts para mejores resultados de código
6. Implementar Agent 06 (Escriba) con Vector DB para vacunas automáticas


## Vacuna #005: Detalle y remediación (consolidado)

# VACUNA #005: Model API Versioning Issues

## Problema
Error 404 al intentar usar `gemini-1.5-flash` con API v1beta de Google Generative AI.

```
Error calling model 'gemini-1.5-flash' (NOT_FOUND): 404 NOT_FOUND.
'models/gemini-1.5-flash is not found for API version v1beta'
```

## Causa Raíz
Los nombres de modelos en langchain-google-genai dependen de la versión de la API de Google.
- `gemini-1.5-flash` y `gemini-1.5-pro` son nombres de API v1, no v1beta
- La librería puede estar usando v1beta internamente, causando mismatch

## Solución / Vacunas Recomendadas

### Opción 1: Usar modelos disponibles en v1beta
```python
VISIONARY_MODEL = "gemini-3-flash-preview"  # Reemplazar gemini-1.5-flash
ARCHITECT_MODEL = "gemini-3-pro-preview"    # Reemplazar gemini-1.5-pro
```

### Opción 2: Crear archivo de configuración
- Centralized `model_config.py` con mapeos de modelos por rol y overrides via `GEMINI_FLASH_MODEL` / `GEMINI_PRO_MODEL`
- Permite cambios rápidos sin tocar código de agentes
- Documentar modelos disponibles según API version

### Opción 3: Validar disponibilidad en tiempo de inicio
```python
# En main.py o graph.py:
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
available_models = [m.name for m in client.models.list_models()]
# Loggear y verificar
```

## Regla de Oro (Agent Developers)
**Nunca hardcodear nombres de modelos en el código del agente.**
Siempre usar un archivo `model_config.py` o variables de entorno que se puedan actualizar sin redeployment.

## Estado Actual
- [x] Identificado problema
- [x] Creado `model_config.py` con mapeos
- [x] Actualizar agent_visionary.py para usar model_config
- [x] Actualizar agent_architect.py para usar model_config
- [x] Actualizar agent_constructor.py para usar model_config
- [ ] Actualizar agent_auditor.py cuando se implemente

## ✅ VACUNA APLICADA EXITOSAMENTE
**Fecha:** 2026-01-11
**Resultado:** Sistema funcionando con Gemini 3 (Flash/Pro Preview) sin errores 404; modelos configurables por entorno.

## Próximos Pasos Completados
1. ✅ Actualizar los agentes para importar de `model_config`
2. ✅ Testear con los nuevos modelos
3. ⏳ Documentar cualquier cambio en comportamiento (latencia, calidad) - En progreso durante testing E2E
