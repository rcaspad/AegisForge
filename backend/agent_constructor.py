"""
Agente 03: El Constructor (Senior Dev)

Responsabilidad:
- Analizar el plan técnico del Arquitecto (Agent 02)
- Generar código de producción en TypeScript, Python, SQL, etc.
- Aplicar "vacunas" (negative constraints) del Escriba (Agent 06) para evitar errores conocidos
- Validar el código contra pautas de seguridad básicas

Modelo: DeepSeek-Coder-V2 o CodeLlama (Local/Privado)
"""

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import List, Dict, Any
import json
import os
from dotenv import load_dotenv
from .model_config import get_model
from .retry_utils import invoke_with_retry

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

class ConstructorAgent:
    """El Constructor: Genera código de producción desde planes técnicos"""
    
    def __init__(self):
        # Vacuna #005: Usar configuración centralizada (Gemini por rol)
        self.model = get_model("constructor")
    
    def generate_code(
        self, 
        plan: str, 
        spec: str, 
        vaccines: List[str],
        messages: List[BaseMessage]
    ) -> Dict[str, Any]:
        """
        Genera código producción desde un plan técnico.
        
        Args:
            plan: Plan técnico del Arquitecto
            spec: Especificación del Visionario
            vaccines: Lista de "reglas negativas" del Escriba (ej: "No uses fs module en Next.js edge")
            messages: Historial de mensajes
            
        Returns:
            {
                "code_generated": str,
                "file_structure": Dict[str, str],  # {filepath: code}
                "warnings": List[str],
                "next_step": str
            }
        """
        
        # Construir prompt con vacunas
        vaccine_context = ""
        if vaccines:
            vaccine_context = "\n\n## RESTRICCIONES DE SEGURIDAD (Vacunas):\n"
            for vaccine in vaccines:
                vaccine_context += f"⚠️ {vaccine}\n"
        
        constructor_prompt = f"""
        Eres El Constructor, un Senior Developer experto en arquitectura limpia y seguridad.
        
        Tu tarea es generar código de producción basado en el siguiente plan técnico.
        
        ## ESPECIFICACIÓN DEL USUARIO:
        {spec}
        
        ## PLAN TÉCNICO DEL ARQUITECTO:
        {plan}
        
        {vaccine_context}
        
        ## INSTRUCCIONES CRÍTICAS:
        1. Genera código modular, tipado y bien documentado
        2. Respeta las restricciones de seguridad (Vacunas) - son críticas
        3. Sigue las mejores prácticas del stack elegido
        4. Estructura el código por archivos (separa controllers, services, models, etc.)
        5. Incluye manejo de errores robusto
        6. Usa naming conventions claros y consistentes
        
        ## FORMATO DE RESPUESTA (IMPORTANTE):
        DEBES devolver SOLAMENTE un objeto JSON válido.
        NO incluyas bloques de markdown (```json), ni texto introductorio, ni explicaciones.
        SOLO EL JSON PURO con la siguiente estructura:

        {{
            "file_structure": {{
                "path/archivo1.ts": "código aquí...",
                "path/archivo2.ts": "código aquí..."
            }},
            "warnings": ["Warning 1", "Warning 2"],
            "next_step": "Descripción breve de qué sigue"
        }}
        """
        
        # Agregar historial de contexto
        messages_for_model = messages + [
            HumanMessage(content=constructor_prompt)
        ]
        
        # Generar respuesta
        response = invoke_with_retry(self.model, messages_for_model)
        
        try:
            # Parsear JSON de la respuesta
            response_text = response.content.strip()
            
            # Intento 1: Eliminar bloques de markdown si existen
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text: # Por si acaso pone solo ```
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Intento 2: Buscar límites del objeto JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                # Intentamos parsear con strict=False para permitir caracteres de control dentro de strings
                # (común en salidas de LLMs que ponen saltos de línea literales en el código)
                result = json.loads(json_str, strict=False)
            else:
                # Si no hay JSON válido, devolver estructura por defecto
                result = {
                    "file_structure": {},
                    "warnings": ["No valid JSON structure found in response"],
                    "next_step": "Reintentar con prompt mejorado"
                }
            
            # Agregar info de depuración
            result["constructor_message"] = response.content
            
            return result
            
        except Exception as e:
            return {
                "file_structure": {},
                "warnings": [f"JSON Parse Error: {str(e)}", "Raw response snippet:", response.content[:1000]],
                "next_step": "Reintentar con formato de salida mejorado",
                "constructor_message": response.content
            }

def constructor_node(state: dict) -> dict:
    """
    Nodo del grafo LangGraph para Agent 03.
    
    Entradas esperadas en `state`:
        - current_plan: Plan técnico del Arquitecto
        - spec_document: Especificación original
        - security_vaccines: Lista de restricciones de seguridad
        - messages: Historial
        
    Salidas en `state`:
        - code_diffs: Código generado estructura de archivos
        - build_status: "clean", "vulnerable", "broken"
    """
    
    constructor = ConstructorAgent()
    
    result = constructor.generate_code(
        plan=state.get("current_plan", ""),
        spec=state.get("spec_document", ""),
        vaccines=state.get("security_vaccines", []),
        messages=state.get("messages", [])
    )
    
    # Evaluar si hay warnings críticos
    build_status = "clean"
    if result.get("warnings"):
        if any("vulnerable" in w.lower() or "security" in w.lower() for w in result["warnings"]):
            build_status = "vulnerable"
        elif any("error" in w.lower() for w in result["warnings"]):
            build_status = "broken"
    
    # Agregar mensaje de respuesta
    state["messages"].append(
        AIMessage(content=f"""
        🏗️ **El Constructor ha generado código**
        
        Archivos generados: {len(result.get('file_structure', {}))}
        Estado: {build_status.upper()}
        
        {f"Warnings: {result.get('warnings', [])}" if result.get('warnings') else ""}
        
        Próximo paso: {result.get('next_step', '')}
        """)
    )
    
    return {
        "code_diffs": list(result.get("file_structure", {}).items()),
        "build_status": build_status,
        "messages": state["messages"]
    }
