import pytest
import httpx

BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200

def test_chat_empty_message():
    payload = {"message": ""}
    response = httpx.post(f"{BASE_URL}/chat", json=payload)
    assert response.status_code == 422 or response.status_code == 400
