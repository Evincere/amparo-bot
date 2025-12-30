import sys
import os

# Agregar directorio actual al path
sys.path.append(os.getcwd())

print("--- CHEQUEO DE ENTORNO ---")

# 1. Chequeo httpx
try:
    import httpx
    print("✅ httpx instalado correctamente")
except ImportError as e:
    print(f"❌ httpx NO estÃ¡ instalado: {e}")

# 2. Chequeo main app structure
try:
    from app.main import app
    print("✅ app.main importado correctamente (Sintaxis OK)")
except Exception as e:
    print(f"❌ Error al importar app.main: {e}")
    import traceback
    traceback.print_exc()

# 3. Chequeo variables globales
try:
    import app.services.chat_service as cs
    print("✅ chat_service importado")
except Exception as e:
    print(f"❌ Error chat_service: {e}")
