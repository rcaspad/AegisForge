# ⚠️ ARCHIVO DEPRECADO - AI Learnings (Versión Antigua)

**NOTA:** Este archivo ha sido reemplazado por `ai_learnings_v2.md` que contiene información consolidada y actualizada.

**Por favor usa:** [`ai_learnings_v2.md`](./ai_learnings_v2.md)

---

## Archivo Original (Solo Referencia Histórica)

Este archivo es la bitácora de errores, lecciones aprendidas y "vacunas" para prevenir la reincidencia de fallos en el sistema multi-agente.

## Historial de Aprendizajes

| ID | Fecha | Agente | Problema | Causa Raíz | Solución / Vacuna |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 000 | 2026-01-11 | N/A | Inicialización | Creación del archivo de memoria. | Mantener este archivo actualizado tras cada fallo. |
| 001 | 2026-01-11 | Agente 03 | TypeError: Failed to fetch en `handleSubmit` | URL del backend hardcoded a `localhost:8000` y falta de manejo de error de red. | Usar variables de entorno para APIs y validar estado del servicio antes de peticiones. |
| 002 | 2026-01-11 | Agente 03 | NotAllowedError: Clipboard API blocked | Intento de uso de `navigator.clipboard.writeText` sin verificar permisos o en contexto restringido (iframe). | Implementar fallback a un modal/input temporal y verificar `navigator.clipboard` antes de usarlo. |
| 003 | 2026-01-11 | Agente 03 | Request Timeout / User Feedback | Peticiones largas (>15s) del Arquitecto causan incertidumbre en el usuario y posibles cortes de red. | Implementar AbortController (90s), lógica de 2 reintentos y contador de latencia en UI para feedback progresivo. |
| 004 | 2026-01-11 | Agente 03 | Failed to fetch recurrente (CORS/Lógica) | El backend está online pero falla en reintentos por configuración de CORS o mal uso de AbortController en recursión. | Blindar CORS en Backend y asegurar que AbortController sea atómico por cada intento de fetch. |

---

## Repositorio de Vacunas (Prompt Injectables)

### Agente 03: El Constructor
- **Regla de Oro (Conectividad):** NUNCA uses URLs hardcoded (ej: `localhost:8000`) para llamadas a API. Utiliza siempre variables de entorno (`process.env.NEXT_PUBLIC_API_URL`).
- **Regla de Oro (Resiliencia de API):** Antes de realizar una petición fetch en una acción de usuario, verifica la disponibilidad del servidor. Si la petición es crítica (como un chat), implementa una política de hasta 2 reintentos con `AbortController`.
- **Regla de Oro (Timeout Management):** Usa `AbortController` para gestionar timeouts explícitos de 90 segundos en llamadas a modelos de IA. Informa al usuario dinámicamente si el proceso supera los 15 segundos para evitar la percepción de "congelamiento".
- **Regla de Oro (Feedback Progresivo):** En peticiones de larga duración, utiliza un contador (`loadingTime`) para actualizar la UI con mensajes específicos sobre el estado del agente (ej: "El Arquitecto está diseñando...").
- **Regla de Oro (Permisos de Navegador):** Antes de usar APIs "sensibles" (Clipboard, Cámara, Geolocalización), verifica si la API existe y envuélvela en un bloque try-catch para manejar `NotAllowedError`. Si falla el Clipboard, muestra el texto en un elemento visible para que el usuario lo copie manualmente.
- **Regla de Oro (CORS Audit - Vacuna #004):** El backend DEBE enviār headers CORS explícitos (`Access-Control-Allow-Origin: *` en desarrollo). En caso de fallos persistentes, inspecciona los headers de respuesta con `response.headers.get('Access-Control-Allow-Origin')`.
- **Regla de Oro (Lógica Atómica - Vacuna #004):** Crea un NUEVO `AbortController` DENTRO de cada iteración del reintento, no fuera del loop. Si reutilizas el controlador, el primer timeout abortará todos los intentos subsiguientes inmediatamente.
- **Regla de Oro (Protocol Consistency - Vacuna #004):** Valida SIEMPRE que `API_URL` incluya el protocolo (`http://` o `https://`). Una URL sin protocolo causa `TypeError` instantáneo en navegadores modernos.

### Agente 04: El Auditor
*(Sin vacunas aún)*

### Agente 05: El Operador
*(Sin vacunas aún)*

- **Regla de Oro (Timeout Management):** Usa `AbortController` para gestionar timeouts explícitos de 90 segundos en llamadas a modelos de IA. Informa al usuario dinámicamente si el proceso supera los 15 segundos para evitar la percepción de "congelamiento".
- **Regla de Oro (Permisos de Navegador):** Antes de usar APIs "sensibles" (Clipboard, Cámara, Geolocalización), verifica si la API existe y envuélvela en un bloque try-catch para manejar `NotAllowedError`. Si falla el Clipboard, muestra el texto en un elemento visible para que el usuario lo copie manualmente.

### Agente 02: El Arquitecto
- **Regla de Oro (CORS):** El middleware de FastAPI debe incluir `allow_origins=["*"]` en desarrollo y restringir a dominios específicos en producción. Asegúrate de que `allow_methods` y `allow_headers` coincidan con las peticiones del frontend.

### Agente 04: El Auditor
*(Sin vacunas aún)*

### Agente 05: El Operador
*(Sin vacunas aún)*
