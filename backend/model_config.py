"""
Configuración centralizada de Modelos (Gemini / Groq)

Soporta múltiples proveedores:
- Google Generative AI (Gemini)
- Groq (Llama, Mixtral)

Controlado por la variable de entorno: LLM_PROVIDER="google" | "groq"
"""

import os
from dotenv import load_dotenv

# Carga variables por si se invoca directamente
load_dotenv()

# Detect active provider (default to google if not set)
PROVIDER = os.getenv("LLM_PROVIDER", "google").lower()

AVAILABLE_MODELS_GOOGLE = {
    "visionary": os.getenv("GEMINI_FLASH_MODEL", "gemini-1.5-flash"),
    "architect": os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-flash"),
    "constructor": os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-flash"),
    "auditor": os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-flash"),
}

AVAILABLE_MODELS_GROQ = {
    "visionary": "llama-3.3-70b-versatile",
    "architect": "llama-3.3-70b-versatile",
    "constructor": "llama-3.3-70b-versatile",
    "auditor": "llama-3.3-70b-versatile",
}

# Parámetros de inferencia por rol
MODEL_PARAMS = {
    "visionary": {
        "temperature": 0.6, 
        "max_tokens": 8192,
        "top_p": 0.95
    },
    "architect": {
        "temperature": 0.2, 
        "max_tokens": 8192
    },
    "constructor": {
        "temperature": 0.4, 
        "max_tokens": 8192
    },
    "auditor": {
        "temperature": 0.1, 
        "max_tokens": 8192
    },
}

# Backwards compatibility variable
AVAILABLE_MODELS = AVAILABLE_MODELS_GROQ if PROVIDER == "groq" else AVAILABLE_MODELS_GOOGLE

def get_model(role: str):
    """
    Factory function que retorna la instancia del modelo correcta
    según el proveedor configurado (Google o Groq).
    """
    
    # Parámetros bases
    params = MODEL_PARAMS.get(role, {"temperature": 0.5, "max_tokens": 4096})
    
    if PROVIDER == "groq":
        from langchain_groq import ChatGroq
        model_name = AVAILABLE_MODELS_GROQ.get(role, "llama3-70b-8192")
        return ChatGroq(
            model=model_name,
            temperature=params.get("temperature", 0.5),
            max_tokens=params.get("max_tokens", 4096),
            api_key=os.getenv("GROQ_API_KEY")
        )
        
    else: # Default to Google
        from langchain_google_genai import ChatGoogleGenerativeAI
        model_name = AVAILABLE_MODELS_GOOGLE.get(role, "gemini-1.5-flash")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=params.get("temperature", 0.5),
            max_tokens=params.get("max_tokens", 4096),
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )