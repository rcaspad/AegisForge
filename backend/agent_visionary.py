from typing import List, Any
from collections import OrderedDict
from langchain_core.messages import SystemMessage, HumanMessage
from .state import ProjectState
import os
from dotenv import load_dotenv
from .model_config import get_model
from .retry_utils import invoke_with_retry

load_dotenv()

# Para desarrollo local, asegúrate de tener GOOGLE_API_KEY en .env
# Vacuna #005: Centralizar configuración de modelos (Gemini por rol)
llm = get_model("visionary")

# Simple LRU cache to reduce duplicate calls and quota usage
VISIONARY_CACHE: OrderedDict[str, Any] = OrderedDict()
CACHE_SIZE = 32

VISIONARY_SYSTEM_PROMPT = """
You are 'El Visionario' (Agent 01), the Product Manager for Aegis Forge.
Your goal is to translate the user's "vibe" or high-level idea into a technical specification document (spec_document).
This document will be the "North Star" for the Architect and Builder agents.

Focus on:
1. Core features and user stories.
2. Technical constraints (if mentioned).
3. Success criteria.

Be concise but thorough. Format the output as a clean Markdown specification.
"""

def visionary_agent(state: ProjectState) -> ProjectState:
    """
    Analyzes user messages and generates/updates the spec_document.
    """
    messages = state.get("messages", [])
    
    # Simple logic: use the last human message or all messages to build the spec
    # In a more advanced version, this would be a multi-turn conversation
    
    # Vaccine #009: Filter empty messages to prevent 'contents are required' error
    valid_messages = [msg for msg in messages if msg.content and msg.content.strip()]
    
    model_messages = [
        SystemMessage(content=VISIONARY_SYSTEM_PROMPT),
        *valid_messages
    ]

    # Generate safe cache key from message contents
    try:
        cache_key = "|".join([f"{m.type}:{m.content}" for m in model_messages if hasattr(m, 'content')])
    except Exception:
        # Fallback to simple hash if join fails
        cache_key = str(hash(str(model_messages)))

    if cache_key in VISIONARY_CACHE:
        VISIONARY_CACHE.move_to_end(cache_key)
        response = VISIONARY_CACHE[cache_key]
    else:
        response = invoke_with_retry(llm, model_messages)
        VISIONARY_CACHE[cache_key] = response
        if len(VISIONARY_CACHE) > CACHE_SIZE:
            VISIONARY_CACHE.popitem(last=False)
    
    # Update the spec document
    # Vaccine #009: Ensure content is string, not list (Gemini can return lists)
    raw_content = response.content if hasattr(response, 'content') else str(response)
    if isinstance(raw_content, list):
        # Join list elements if it's a multimodal response
        spec_content = "\n".join([str(item) for item in raw_content])
    else:
        spec_content = str(raw_content)

    # Return state updates - operator.add will handle message concatenation
    return {
        "spec_document": spec_content, # Ensure this is always a string
        "messages": [response]
    }
