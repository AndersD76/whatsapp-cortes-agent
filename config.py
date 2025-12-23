import os
from dotenv import load_dotenv

load_dotenv()

# Evolution API Configuration
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "sua-api-key-aqui")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "whatsapp-cortes")

# Paths
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "cortes.csv")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
