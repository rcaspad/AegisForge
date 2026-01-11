from typing import List, Any
from collections import OrderedDict
from langchain_core.messages import SystemMessage
from .state import ProjectState, Task
import json
import os
from dotenv import load_dotenv
from .model_config import get_model
from .retry_utils import invoke_with_retry

load_dotenv()

# Vacuna #005: Usar configuración centralizada de modelos Gemini por rol
llm = get_model("architect")

ARCHITECT_CACHE: OrderedDict[str, Any] = OrderedDict()
CACHE_SIZE = 32

ARCHITECT_SYSTEM_PROMPT = """
You are 'El Arquitecto' (Agent 02), the Tech Lead for Aegis Forge.
Your goal is to take the Technical Specification (spec_document) and design a implementation plan.

Tasks:
1. Define the directory structure.
2. Break down the project into small, actionable tasks for the Builder agent.
3. Each task must have a unique ID and a clear description.

Output Format:
You MUST return a JSON object with a 'tasks' key, containing a list of task objects.
Each task object MUST have: 'id' (string), 'description' (string), 'status' (string, default "pending").

Example Output:
{
  "tasks": [
    {"id": "TASK-001", "description": "Initialize database schema using Prisma", "status": "pending"},
    {"id": "TASK-002", "description": "Create Auth API endpoints", "status": "pending"}
  ]
}

DO NOT include any other text in your response, ONLY the JSON object.
"""

def architect_agent(state: ProjectState) -> ProjectState:
    """
    Consumes the spec_document and generates the current_plan.
    """
    spec = state.get("spec_document", "")
    
    # Vaccine #009: Defensive coding against list-in-spec bug
    if isinstance(spec, list):
        spec = "\n".join([str(s) for s in spec])
    else:
        spec = str(spec)
    
    # Check if spec is empty (initial check)
    if not spec or not str(spec).strip():
        return state 

    # Construct Raw Messages
    raw_messages = [
        SystemMessage(content=ARCHITECT_SYSTEM_PROMPT.strip()),
        SystemMessage(content=f"SPECIFICATION DOCUMENT:\n{spec.strip()}")
    ]
    
    # --- BLOQUE DE CORRECCIÓN (SANITIZACIÓN) ---
    # Filtramos mensajes para asegurar que NINGUNO esté vacío antes de llamar a Google
    model_messages = []
    for msg in raw_messages:
        if msg.content and str(msg.content).strip():
            model_messages.append(msg)
            
    # Si después de filtrar no queda nada, abortamos para evitar el crash
    if not model_messages:
        return state
    # -------------------------------------------

    # Generate safe cache key
    cache_key = f"architect:{hash(spec[:200])}"  # Use hash of first 200 chars to avoid issues

    if cache_key in ARCHITECT_CACHE:
        ARCHITECT_CACHE.move_to_end(cache_key)
        response = ARCHITECT_CACHE[cache_key]
    else:
        # Usamos la lista filtrada 'model_messages'
        response = invoke_with_retry(llm, model_messages)
        ARCHITECT_CACHE[cache_key] = response
        if len(ARCHITECT_CACHE) > CACHE_SIZE:
            ARCHITECT_CACHE.popitem(last=False)
    
    try:
        # Extract JSON from response. content might be wrapped in ```json ... ```
        # Vaccine #009: Safe content extraction
        if hasattr(response, 'content'):
            content = str(response.content).strip() if response.content else ""
        else:
            content = str(response).strip()
            
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        plan_data = json.loads(content)
        tasks = plan_data.get("tasks", [])
        
        # Ensure status is set
        for task in tasks:
            if "status" not in task:
                task["status"] = "pending"
                
        # Return only the fields we're updating
        return {"current_plan": tasks}
    except Exception as e:
        print(f"Error parsing architect plan: {e}")
        # Return empty plan on error
        return {"current_plan": []}