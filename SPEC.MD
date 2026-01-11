# SPEC.MD: Project "Aegis Forge" - Autonomous Vibe Coding SaaS
**Versión:** 1.0.0 | **Estado:** Aprobado para Diseño | **Enfoque:** Enterprise/SOC2

## 1. Resumen Ejecutivo
Plataforma SaaS de "Caja Negra" que permite a fundadores no técnicos crear software de producción crítica mediante lenguaje natural. A diferencia de los editores de código (Cursor) o generadores de prototipos (Lovable), este sistema actúa como una **Consultora de Software Autónoma**: gestiona el ciclo de vida completo, desde la toma de requisitos hasta el despliegue en la nube del cliente (AWS/GCP), garantizando estándares de seguridad SOC2 y auto-reparación mediante una arquitectura híbrida de IA.

## 2. Principios de Arquitectura
1.  **Abstracción Radical:** El usuario *nunca* ve el código, solo ve "Capacidades" y "Estado del Sistema".
2.  **Seguridad Paranoica (Zero Trust):** Todo código generado se considera hostil hasta que pasa la auditoría del Agente 04 en un entorno aislado (Sandbox).
3.  **Memoria Inmunológica:** Los errores no se descartan; se procesan para crear "vacunas" (reglas de contexto) que previenen la reincidencia.
4.  **Hybrid Intelligence:** Velocidad en la interacción (Cloud AI) + Privacidad/Seguridad en la ejecución (Local AI).

## 3. Arquitectura del Sistema Multi-Agente (The Hexagon)
El sistema utiliza el **Model Context Protocol (MCP)** para estandarizar la comunicación entre agentes y herramientas.

### Los 6 Agentes Especializados

* **Agente 01: El Visionario (Product Manager)**
    * **Modelo:** Gemini 1.5 Flash / Groq (Llama-3-70b).
    * **Función:** Interfaz de chat de baja latencia. Traduce "vibras" en especificaciones técnicas estructuradas. Gestiona la aprobación del usuario.
    * **Herramientas:** Historial de chat, Gestor de Estado del Proyecto.

* **Agente 02: El Arquitecto (Tech Lead)**
    * **Modelo:** Gemini 1.5 Pro (Alta ventana de contexto).
    * **Función:** Decide el stack tecnológico, diseña esquemas de base de datos y define la estructura de archivos.
    * **Herramientas:** Knowledge Base de Arquitecturas Seguras.

* **Agente 03: El Constructor (Senior Dev)**
    * **Modelo:** DeepSeek-Coder-V2 / CodeLlama (Local/Privado en GPU Cluster).
    * **Función:** Ejecuta la escritura de código, migraciones de DB y scripts de configuración.
    * **Entorno:** Contenedor efímero sin acceso a internet abierto.

* **Agente 04: El Auditor (Security & QA - "El Policía")**
    * **Modelo:** Modelo Local Fine-tuneado en CVEs y OWASP (Ej. StarCoder2-Sec).
    * **Función:** Análisis estático (SAST), intentos de inyección de dependencias, revisión de cumplimiento SOC2. **Tiene poder de veto.**
    * **Herramientas:** SonarQube, Trivy, Sandbox Execution.

* **Agente 05: El Operador (DevOps/SRE)**
    * **Modelo:** Gemini 1.5 Pro.
    * **Función:** Gestiona Terraform/Pulumi para desplegar en la cuenta AWS/GCP del cliente. Maneja claves API y secretos.
    * **Herramientas:** AWS SDK, Google Cloud CLI, Terraform.

* **Agente 06: El Escriba (Knowledge Manager - "El Inmunólogo")**
    * **Modelo:** Modelo ligero de resumen (Mistral Small o similar).
    * **Trigger:** Se activa *solo* cuando ocurre un error (build fallido, test fallido, veto del Auditor).
    * **Proceso:**
        1.  Analiza el log del error y el código causante.
        2.  Genera una "Vacuna": Una regla de texto o patrón de código negativo.
        3.  Almacena la vacuna en la base de datos vectorial (RAG).
    * **Resultado:** En futuros proyectos, el Agente 03 recibe estas vacunas en su contexto ("No hagas X, porque en el pasado causó el error Y").

## 4. Flujo de Trabajo (The Assembly Line)

1.  **Fase de Intención:** Usuario habla con *El Visionario*. Se genera un `spec.json`.
2.  **Fase de Planificación:** *El Arquitecto* consume el spec y diseña la solución.
3.  **Fase de Construcción (Loop Crítico):**
    * *El Constructor* escribe código en microVMs (Firecracker).
    * *El Auditor* escanea el código.
    * **Si Falla:** *El Escriba* genera vacuna -> Se notifica al *Constructor* -> Reintento.
    * **Si Pasa:** Se hace commit al repositorio gestionado.
4.  **Fase de Despliegue:** *El Operador* empuja cambios a la nube del cliente.
5.  **Fase "Human-in-the-Loop" (Opcional):** Si el ciclo de auto-reparación falla 3 veces, se alerta al equipo de soporte humano (Servicio Premium).

## 5. Stack Tecnológico

### Frontend (Usuario)
* **Interfaz:** Next.js (React) + Vercel AI SDK (Streaming de texto).
* **Voice:** OpenAI Whisper (para input de voz de los fundadores).

### Backend (Orquestación & IA)
* **Orquestador:** **LangGraph** (Python). Es ideal para flujos cíclicos y con estado (stateful) como este.
* **Protocolo de Herramientas:** **MCP (Model Context Protocol)**. Permite que los agentes locales y en la nube usen las mismas herramientas de sistema de archivos y terminal.
* **Inferencia Rápida:** API de Groq o Gemini Flash.
* **Inferencia Pesada/Privada:** Cluster de GPUs (NVIDIA A100/H100) ejecutando **vLLM** para servir modelos open-source (DeepSeek, Llama 3) de forma privada.

### Infraestructura de Seguridad (Sandboxing)
* **MicroVMs:** **AWS Firecracker** o **Fly.io Machines**. Cada sesión de codificación ocurre en una máquina virtual que se destruye al terminar. Esto evita que un código malicioso generado por la IA escape al servidor principal.

### Datos & Memoria
* **Base de Datos Relacional:** PostgreSQL (Usuarios, Proyectos, Facturación).
* **Base de Datos Vectorial:** **Qdrant** o **Weaviate**. Aquí vive el "Sistema Inmunológico" (las vacunas generadas por El Escriba).

## 6. Modelo de Datos: "Las Vacunas"

El aporte clave del Agente 06 requiere un esquema específico en la Vector DB:

```json
{
  "collection": "project_vaccines",
  "payload": {
    "error_pattern": "ReferenceError en React useEffect con dependencia faltante",
    "context_embedding": [vector...],
    "solution_instruction": "Asegurar que todas las variables externas usadas dentro de useEffect estén en el array de dependencias o usar useRef.",
    "severity": "High",
    "origin_agent": "Agent-03",
    "created_at": "2026-01-12"
  }
}
```
## TECHNICAL IMPLEMENTATION GUIDELINES

### A. Model Serving Layer
- **Local Models (DeepSeek/CodeLlama):** MUST be served via **vLLM** to support concurrent generation requests from Agent 03.
- **Context Handling:** Agent 01 MUST use Gemini's caching feature for project history to reduce latency and cost.

### B. LangGraph State Schema
The Shared State object passed between agents must strictly adhere to:
```python
class ProjectState(TypedDict):
    messages: List[BaseMessage]
    spec_document: str          # The immutable "North Star"
    current_plan: List[Task]    # Generated by Architect
    code_diffs: List[FileDiff]  # Proposed changes by Builder
    security_vaccines: List[str]# Context injected by Scribe
    retry_count: int            # For HITL trigger
    build_status: str           # "clean", "vulnerable", "broken"
C. The "Scribe" Interface (Agent 06)
When an error occurs, the Scribe DOES NOT fix the code. It creates a Vector Embedding:

Input: Error Log + Failing Code Snippet.

Output: A natural language "Negative Constraint" (e.g., "Do not use 'fs' module directly in Next.js edge functions").

Storage: Upsert to Qdrant collection global_vaccines.

D. File System Authority
Agents CANNOT interact with the OS directly.

All file operations MUST go through the MCP Filesystem Server.

This server enforces the Sandbox Boundary: No access outside /app/workplace.

## 7. Operational Safeguards (Vaccines #005-#007)

- **Model Config (Vacuna #005):** Todos los agentes deben obtener el modelo y parámetros desde `backend/model_config.py`; prohibido hardcodear nombres de modelo.
- **Quota Resilience (Vacunas #006-#007):**
    - Rate limiting en backend `/chat`: slowapi 5 req/min por IP para evitar bursts.
    - Reintentos con backoff exponencial (`tenacity`) en Visionary, Architect y Constructor (3 intentos máx.).
    - Caché LRU para prompts idénticos en agentes y en `/chat` para reducir llamadas repetidas.
    - Si se mantiene la presión de uso, considerar upgrade a Gemini paid tier.