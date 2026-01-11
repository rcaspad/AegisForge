import os
import io
import json
import zipfile
import logging
import re
from typing import Dict, List, Any, Optional
from collections import OrderedDict

# Framework Imports
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain / AI Imports
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Rate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# 1. CONFIGURACIÓN E INICIALIZACIÓN
# Cargar .env desde la raíz del proyecto
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Configurar Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

# Intentar importar el grafo (LangGraph)
try:
    from .graph import graph
except ImportError as e:
    logger.error(f"⚠️ Error importando graph: {e}. Asegúrate de ejecutar con uvicorn backend.main:app")
    graph = None

# Inicializar App
app = FastAPI(title="Aegis Forge Backend")

# 2. RATE LIMITING (Protección contra abuso)
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

def _rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please retry shortly."},
    )
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. CORS (Configuración para Vercel y Localhost)
def get_allowed_origins():
    # Lee variable de entorno ALLOWED_ORIGINS (si existe en Render)
    env_origins = os.getenv("ALLOWED_ORIGINS")
    default_origins = [
        "http://localhost:3000",         # Desarrollo Local
        "https://aegis-forge.vercel.app" # Producción Vercel
    ]
    
    if env_origins:
        additional = [o.strip() for o in env_origins.split(",") if o.strip()]
        return list(set(default_origins + additional))
    
    return default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=r"^https://.*\.vercel\.app$", # Permite cualquier preview de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. MODELOS DE DATOS (Pydantic)
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"

class ExportRequest(BaseModel):
    files: Dict[str, str]

class RefineRequest(BaseModel):
    instruction: str
    current_files: Dict[str, str]

# 5. CACHÉ SIMPLE (LRU)
CHAT_CACHE: OrderedDict[str, dict] = OrderedDict()
CACHE_SIZE = 20

# 6. ENDPOINTS

@app.get("/")
def read_root():
    """Health Check Endpoint"""
    return {"status": "Backend Online", "service": "Aegis Forge V1.0"}

@app.post("/chat")
@limiter.limit("5/minute")
async def chat(request: Request, payload: ChatRequest):
    if not graph:
        raise HTTPException(status_code=500, detail="El Grafo de IA no se cargó correctamente.")

    # Verificar Caché
    cache_key = payload.message.strip()
    if cache_key in CHAT_CACHE:
        CHAT_CACHE.move_to_end(cache_key)
        return CHAT_CACHE[cache_key]

    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    # Estado inicial para LangGraph
    initial_state = {
        "messages": [HumanMessage(content=payload.message.strip())],
        "spec_document": "",
        "current_plan": [],
        "code_diffs": [],
        "retry_count": 0,
        "build_status": "clean"
    }

    try:
        # Ejecutar el agente
        result = graph.invoke(initial_state)
        
        # Procesar respuesta
        last_message = result["messages"][-1]
        
        # Formatear código generado
        code_diffs = []
        if result.get("code_diffs"):
            for item in result["code_diffs"]:
                if isinstance(item, tuple):
                    code_diffs.append({"filepath": item[0], "content": item[1]})
                elif isinstance(item, dict):
                    filepath = item.get("filepath", item.get("file_path", ""))
                    content = item.get("content", item.get("code", ""))
                    code_diffs.append({"filepath": filepath, "content": content})

        response_payload = {
            "response": last_message.content,
            "spec_document": result.get("spec_document", ""),
            "plan": result.get("current_plan", []),
            "code_generated": code_diffs,
            "build_status": result.get("build_status", "clean")
        }

        # Guardar en caché
        CHAT_CACHE[cache_key] = response_payload
        if len(CHAT_CACHE) > CACHE_SIZE:
            CHAT_CACHE.popitem(last=False)

        return response_payload

    except Exception as e:
        logger.error(f"Error en /chat: {str(e)}")
        # Manejo de error de cuota de Gemini
        if "429" in str(e) or "ResourceExhausted" in str(e):
            raise HTTPException(status_code=429, detail="Cuota de IA excedida. Intenta más tarde.")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export")
async def export_project(data: ExportRequest):
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path, content in data.files.items():
                clean_path = file_path.replace("\\", "/") # Windows fix
                zip_file.writestr(clean_path, content)
        
        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=aegis_project.zip"}
        )
    except Exception as e:
        logger.error(f"Error exportando ZIP: {e}")
        raise HTTPException(status_code=500, detail="Error generando el archivo ZIP")

@app.post("/refine")
async def refine_code(request: RefineRequest):
    print(f"🔧 Refinando código: {request.instruction}")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Falta GEMINI_API_KEY en variables de entorno")

    prompt = f"""
    ACT AS: Senior Code Refactorer.
    CONTEXT: {json.dumps(request.current_files, indent=2)}
    INSTRUCTION: {request.instruction}
    TASK: Rewrite ONLY the files that need modification.
    OUTPUT: Valid JSON {{ "filename": "new content" }}.
    """

    try:
        refine_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=api_key
        )
        
        response = refine_llm.invoke(prompt)
        content = str(response.content).strip()
        
        # Limpieza de JSON (Markdown fix)
        if content.startswith("```json"): content = content[7:-3].strip()
        if content.startswith("```"): content = content[3:-3].strip()
        
        new_files = json.loads(content)
        return {"success": True, "modified_files": new_files}
        
    except Exception as e:
        logger.error(f"Error en refinamiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error al refinar código: {str(e)}")

# --- FIN DEL ARCHIVO ---