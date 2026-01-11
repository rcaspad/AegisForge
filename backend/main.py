
# 1. IMPORTS
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import io
import zipfile
import os
from collections import OrderedDict
import logging
from model_config import get_model
from langchain_core.messages import HumanMessage, AIMessage
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# 2. INICIALIZACIÓN DE LA APP
app = FastAPI()
logger = logging.getLogger(__name__)

# 3. CONFIGURACIÓN CORS
import re
# --- CORS CONFIG (Render/Prod Ready) ---
def get_allowed_origins():
    env_origins = os.getenv("ALLOWED_ORIGINS")
    default_origins = [
        "http://localhost:3000",
        "https://aegis-forge.vercel.app"
    ]
    if env_origins:
        # Split by comma, strip whitespace, and merge with defaults (no duplicates)
        env_list = [o.strip() for o in env_origins.split(",") if o.strip()]
        return list(set(default_origins + env_list))
    return default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=r"^https://([a-zA-Z0-9-]+\\.)?vercel\\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. MODELOS DE DATOS
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"

class ExportRequest(BaseModel):
    files: Dict[str, str]

class RefineRequest(BaseModel):
    instruction: str
    current_files: Dict[str, str]

# 5. ENDPOINTS
@app.get("/")
def read_root() -> dict:
    return {"status": "Backend Online", "service": "Aegis Forge"}


# --- ENDPOINT /chat ---
# Lightweight LRU cache to avoid re-hitting LLMs for repeated prompts
CHAT_CACHE: OrderedDict[str, dict] = OrderedDict()
CACHE_SIZE = 20

try:
    from google.api_core.exceptions import ResourceExhausted
except ImportError:
    class ResourceExhausted(Exception):
        pass

try:
    from .graph import graph  # type: ignore
except ImportError:
    print("\n❌ ERROR: No ejecutes 'python main.py' directamente.")
    print("✅ Usa: uvicorn backend.main:app --host 0.0.0.0 --port 8000\n")
    import sys
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found!")
else:
    print("SUCCESS: GOOGLE_API_KEY loaded.")

# Rate limiting (Vaccine #006) to protect against quota exhaustion
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

def _rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please retry shortly."},
    )

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("5/minute")
async def chat(request: Request, payload: ChatRequest):
    cache_key = payload.message.strip()
    if cache_key in CHAT_CACHE:
        CHAT_CACHE.move_to_end(cache_key)
        return CHAT_CACHE[cache_key]

    # Vaccine #009: Validate message content before processing
    if not payload.message or not payload.message.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Message content cannot be empty"},
        )
    initial_state = {
        "messages": [HumanMessage(content=payload.message.strip())],
        "spec_document": "",
        "current_plan": [],
        "code_diffs": [],
        "security_vaccines": [],
        "retry_count": 0,
        "build_status": "clean"
    }
    try:
        result = graph.invoke(initial_state)
    except ResourceExhausted as exc:
        logger.warning("Gemini quota hit: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Gemini quota exceeded. Please retry after a short wait or reduce request frequency.",
                "error": str(exc),
            },
        )
    except Exception as exc:
        logger.exception("Unhandled error in /chat")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Backend error while processing request.", "error": str(exc)},
        )
    last_message = result["messages"][-1]
    code_diffs = []
    if result.get("code_diffs"):
        for item in result["code_diffs"]:
            if isinstance(item, tuple):
                code_diffs.append({"filepath": item[0], "content": item[1]})
            elif isinstance(item, dict):
                if "code" in item and "content" not in item:
                    code_diffs.append({"filepath": item.get("filepath", item.get("file_path", "")), "content": item["code"]})
                else:
                    code_diffs.append(item)
    payload_out = {
        "response": last_message.content,
        "spec_document": result["spec_document"],
        "plan": result["current_plan"],
        "code_generated": code_diffs,
        "build_status": result.get("build_status", "clean")
    }
    CHAT_CACHE[cache_key] = payload_out
    if len(CHAT_CACHE) > CACHE_SIZE:
        CHAT_CACHE.popitem(last=False)
    return payload_out

@app.post("/export")
async def export_project(data: ExportRequest):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, content in data.files.items():
            clean_path = file_path.replace("\\", "/")
            zip_file.writestr(clean_path, content)
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=aegis_project.zip"}
    )

@app.post("/refine")
async def refine_code(request: RefineRequest):
    print(f"🔧 Refinando código con instrucción: {request.instruction}")
    # 1. Preparar contexto (Código actual + Instrucción)
    files_context = json.dumps(request.current_files, indent=2)
    # 2. Prompt de Ingeniería para "Cirugía de Código"
    prompt = f"""
    ACT AS: Senior Code Refactorer & Architect.
    
    CONTEXT (Current Codebase):
    {files_context}
    
    USER INSTRUCTION:
    {request.instruction}
    
    TASK:
    1. Analyze the instruction and the current code.
    2. Rewrite ONLY the files that need changes to fulfill the instruction.
    3. You can create NEW files if necessary.
    
    OUTPUT FORMAT:
    Return a pure JSON object mapping filenames to their NEW content.
    Example: {{ "src/utils/auth.ts": "export const..." }}
    
    CRITICAL:
    - Return VALID JSON only. No markdown formatting like ```json.
    - Do NOT return files that remained unchanged.
    """
    try:
        # 3. Instanciar LLM rápido (Flash) para cambios ágiles
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Falta GEMINI_API_KEY en backend")
        refine_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=api_key
        )
        # 4. Invocar a la IA
        response = refine_llm.invoke(prompt)
        content = response.content
        # 5. Limpieza de JSON (Nuestra técnica clásica antibasura)
        if hasattr(content, 'content'):
            content = content.content
        content = str(content).strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        if content.startswith("```"):
            content = content[3:-3].strip()
        # 6. Parsear y devolver
        new_files = json.loads(content)
        return {"success": True, "modified_files": new_files}
    except Exception as e:
        print(f"🔥 Error en refinamiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error refactorizando: {str(e)}")
# Vaccine #008: Backend must run as package via uvicorn, not as direct script
try:
    from .graph import graph  # type: ignore
except ImportError:
    print("\n❌ ERROR: No ejecutes 'python main.py' directamente.")
    print("✅ Usa: uvicorn backend.main:app --host 0.0.0.0 --port 8000\n")
    import sys
    sys.exit(1)
from langchain_core.messages import HumanMessage, AIMessage
import os
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from collections import OrderedDict
import logging

try:
    from google.api_core.exceptions import ResourceExhausted
except ImportError:
    # If the library is missing, we define a dummy exception so we don't catch ALL exceptions
    class ResourceExhausted(Exception):
        pass
except Exception: 
    # Fallback for other import errors
    class ResourceExhausted(Exception):
        pass

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found!")
else:
    print("SUCCESS: GOOGLE_API_KEY loaded.")

app = FastAPI()
logger = logging.getLogger(__name__)

# Rate limiting (Vaccine #006) to protect against quota exhaustion
# Increased default limit to prevent health check blocking
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

def _rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please retry shortly."},
    )

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware (Vaccine #004: CORS Audit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all. In production, restrict to specific frontend URL.
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "X-Total-Count"],
    max_age=600,  # Cache preflight for 10 minutes
)

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"


# Lightweight LRU cache to avoid re-hitting LLMs for repeated prompts
CHAT_CACHE: OrderedDict[str, dict] = OrderedDict()
CACHE_SIZE = 20

@app.get("/")
@limiter.exempt
async def root():
    # Align with docs: return a simple status object
    return {"status": "ok"}

@app.post("/chat")
@limiter.limit("5/minute")
async def chat(request: Request, payload: ChatRequest):
    cache_key = payload.message.strip()
    if cache_key in CHAT_CACHE:
        CHAT_CACHE.move_to_end(cache_key)
        return CHAT_CACHE[cache_key]

    # Vaccine #009: Validate message content before processing
    if not payload.message or not payload.message.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Message content cannot be empty"},
        )
    
    # Prepare initial state
    initial_state = {
        "messages": [HumanMessage(content=payload.message.strip())],
        "spec_document": "",
        "current_plan": [],
        "code_diffs": [],
        "security_vaccines": [],
        "retry_count": 0,
        "build_status": "clean"
    }
    
    try:
        # Run graph
        # In a real scenario, we'd use thread_id and checkpointer
        result = graph.invoke(initial_state)
    except ResourceExhausted as exc:  # Gemini quota
        logger.warning("Gemini quota hit: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Gemini quota exceeded. Please retry after a short wait or reduce request frequency.",
                "error": str(exc),
            },
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("Unhandled error in /chat")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Backend error while processing request.", "error": str(exc)},
        )
    
    # Extract the last AI message and spec_document
    last_message = result["messages"][-1]
    
    # Format code_diffs for frontend (from list of tuples to list of dicts)
    code_diffs = []
    if result.get("code_diffs"):
        for item in result["code_diffs"]:
            if isinstance(item, tuple):
                # Use 'content' key to match frontend expectations
                code_diffs.append({"filepath": item[0], "content": item[1]})
            elif isinstance(item, dict):
                # Normalize key name if backend produced 'code'
                if "code" in item and "content" not in item:
                    code_diffs.append({"filepath": item.get("filepath", item.get("file_path", "")), "content": item["code"]})
                else:
                    code_diffs.append(item)

    payload = {
        "response": last_message.content,
        "spec_document": result["spec_document"],
        "plan": result["current_plan"],
        "code_generated": code_diffs,
        "build_status": result.get("build_status", "clean")
    }

    CHAT_CACHE[cache_key] = payload
    if len(CHAT_CACHE) > CACHE_SIZE:
        CHAT_CACHE.popitem(last=False)

    return payload

if __name__ == "__main__":
    # Para desarrollo local únicamente. Render usará el comando recomendado:
    # uvicorn backend.main:app --host 0.0.0.0 --port 8000
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
