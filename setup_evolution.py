"""
Script para configurar a instância no Evolution API.
Execute após o deploy no Railway.

Uso: python setup_evolution.py
"""
import httpx
import sys
import json

# Configurações - EDITE CONFORME NECESSÁRIO
EVOLUTION_API_URL = "https://SUA-URL-EVOLUTION.up.railway.app"  # URL do Evolution no Railway
EVOLUTION_API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
INSTANCE_NAME = "whatsapp-cortes"
WEBHOOK_URL = "https://SUA-URL-AGENTE.up.railway.app/webhook"  # URL do Agente no Railway


def criar_instancia():
    """Cria uma nova instância no Evolution API."""
    url = f"{EVOLUTION_API_URL}/instance/create"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "instanceName": INSTANCE_NAME,
        "integration": "WHATSAPP-BAILEYS",
        "qrcode": True,
        "webhook": {
            "url": WEBHOOK_URL,
            "webhookByEvents": False,
            "webhookBase64": False,
            "events": [
                "MESSAGES_UPSERT"
            ]
        }
    }

    print(f"Criando instância '{INSTANCE_NAME}'...")
    response = httpx.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code in [200, 201]:
        data = response.json()
        print("✅ Instância criada com sucesso!")
        if "qrcode" in data:
            print(f"\n📱 QR Code (base64):\n{data['qrcode'].get('base64', 'N/A')[:100]}...")
        return data
    else:
        print(f"❌ Erro ao criar instância: {response.status_code}")
        print(response.text)
        return None


def obter_qrcode():
    """Obtém o QR Code para conectar o WhatsApp."""
    url = f"{EVOLUTION_API_URL}/instance/connect/{INSTANCE_NAME}"
    headers = {"apikey": EVOLUTION_API_KEY}

    print(f"\nObtendo QR Code...")
    response = httpx.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        if "base64" in data:
            print("✅ QR Code obtido!")
            print(f"\n📱 Escaneie o QR Code no link abaixo:")
            print(f"{EVOLUTION_API_URL}/instance/connect/{INSTANCE_NAME}")

            # Salva QR code em arquivo HTML para facilitar
            html = f'''
            <html>
            <head><title>QR Code - {INSTANCE_NAME}</title></head>
            <body style="display:flex;justify-content:center;align-items:center;height:100vh;background:#1a1a1a;">
                <div style="text-align:center;color:white;">
                    <h2>Escaneie o QR Code com WhatsApp</h2>
                    <img src="{data['base64']}" style="width:300px;height:300px;"/>
                    <p>Instância: {INSTANCE_NAME}</p>
                </div>
            </body>
            </html>
            '''
            with open("qrcode.html", "w") as f:
                f.write(html)
            print("📄 QR Code salvo em: qrcode.html")

        return data
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        return None


def verificar_conexao():
    """Verifica se a instância está conectada."""
    url = f"{EVOLUTION_API_URL}/instance/connectionState/{INSTANCE_NAME}"
    headers = {"apikey": EVOLUTION_API_KEY}

    response = httpx.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        state = data.get("state", "unknown")
        print(f"\n📊 Status da conexão: {state}")
        return state == "open"
    return False


def configurar_webhook():
    """Configura o webhook da instância."""
    url = f"{EVOLUTION_API_URL}/webhook/set/{INSTANCE_NAME}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "url": WEBHOOK_URL,
        "webhookByEvents": False,
        "webhookBase64": False,
        "events": [
            "MESSAGES_UPSERT"
        ]
    }

    print(f"\nConfigurando webhook: {WEBHOOK_URL}")
    response = httpx.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code in [200, 201]:
        print("✅ Webhook configurado!")
        return True
    else:
        print(f"❌ Erro: {response.status_code}")
        print(response.text)
        return False


def main():
    print("=" * 50)
    print("SETUP - Evolution API + Agente de Cortes")
    print("=" * 50)

    if "SUA-URL" in EVOLUTION_API_URL or "SUA-URL" in WEBHOOK_URL:
        print("\n⚠️  ATENÇÃO: Edite este arquivo e configure as URLs!")
        print(f"   EVOLUTION_API_URL = URL do Evolution no Railway")
        print(f"   WEBHOOK_URL = URL do Agente de Cortes no Railway")
        sys.exit(1)

    print(f"\n📌 Evolution API: {EVOLUTION_API_URL}")
    print(f"📌 Webhook URL: {WEBHOOK_URL}")
    print(f"📌 Instância: {INSTANCE_NAME}")

    # Tenta criar instância
    resultado = criar_instancia()

    if resultado:
        # Obtém QR Code
        obter_qrcode()

        print("\n" + "=" * 50)
        print("PRÓXIMOS PASSOS:")
        print("1. Abra qrcode.html no navegador")
        print("2. Escaneie o QR Code com seu WhatsApp")
        print("3. Envie 'status' para o número conectado")
        print("=" * 50)


if __name__ == "__main__":
    main()
