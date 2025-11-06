# app/main.py
from fastapi import FastAPI
from app.routers import webhook
from app.config import settings
from app.routers import webhook, dashboard
from app.routers import dashboard
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

# Teste opcional (pode remover depois)
print("🔍 Variável WHATS_GROUP_ID:", os.getenv("WHATS_GROUP_ID"))

app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    description="Backend base para o assistente inteligente de atendimento via WhatsApp",
    version=settings.VERSION,
)

@app.get("/")
def home():
    return {"status": "ok", "mensagem": f"{settings.PROJECT_NAME} rodando com sucesso 🚀"}

# Inclui o router do webhook
# === ROTAS PRINCIPAIS ===
app.include_router(webhook.router, tags=["webhook"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


