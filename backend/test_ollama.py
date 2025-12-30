import asyncio
import httpx
from app.config import settings

async def test_ollama():
    print(f"--- TESTING OLLAMA CONNECTION ---")
    print(f"Host: {settings.ollama_host}")
    print(f"Model: {settings.ollama_model}")
    print(f"SSL Verify: {settings.ssl_verify}")
    
    url = f"{settings.ollama_host}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": "Hola"}],
        "stream": False
    }
    headers = {'Authorization': f'Bearer {settings.ollama_api_key}'}
    
    print(f"Sending request to {url}...")
    
    try:
        async with httpx.AsyncClient(verify=settings.ssl_verify) as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            response.raise_for_status()
            print("✅ SUCCESS!")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
