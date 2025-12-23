from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import HOST, PORT

from .whatsapp import whatsapp_client
from .commands import processar_comando

app = FastAPI(
    title="WhatsApp Cortes Agent",
    description="Agente para controle de cortes de produção via WhatsApp",
    version="1.0.0"
)


async def processar_mensagem(numero: str, texto: str):
    """Processa a mensagem e envia a resposta."""
    # Processa o comando
    resposta = processar_comando(texto)

    # Envia a resposta via WhatsApp
    await whatsapp_client.enviar_mensagem(numero, resposta)


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """Endpoint para receber webhooks da Evolution API."""
    try:
        payload = await request.json()

        # Extrai dados da mensagem
        dados = whatsapp_client.extrair_dados_webhook(payload)

        # Ignora se houver erro na extração
        if "erro" in dados:
            return JSONResponse({"status": "error", "message": dados["erro"]})

        # Ignora mensagens enviadas por mim mesmo
        if dados.get("from_me", False):
            return JSONResponse({"status": "ignored", "reason": "own_message"})

        # Ignora mensagens de grupo (opcional)
        if dados.get("is_group", False):
            return JSONResponse({"status": "ignored", "reason": "group_message"})

        # Ignora mensagens vazias
        texto = dados.get("texto", "").strip()
        if not texto:
            return JSONResponse({"status": "ignored", "reason": "empty_message"})

        numero = dados.get("numero", "")
        if not numero:
            return JSONResponse({"status": "ignored", "reason": "no_number"})

        # Processa a mensagem em background para responder rápido ao webhook
        background_tasks.add_task(processar_mensagem, numero, texto)

        return JSONResponse({"status": "ok", "message": "processing"})

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})


@app.get("/")
async def root():
    """Endpoint de verificação."""
    return {
        "status": "online",
        "service": "WhatsApp Cortes Agent",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )
