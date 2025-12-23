import httpx
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE


class WhatsAppClient:
    def __init__(self):
        self.base_url = EVOLUTION_API_URL
        self.api_key = EVOLUTION_API_KEY
        self.instance = EVOLUTION_INSTANCE
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    async def enviar_mensagem(self, numero: str, mensagem: str) -> dict:
        """Envia uma mensagem de texto via Evolution API."""
        url = f"{self.base_url}/message/sendText/{self.instance}"

        # Formata o número (remove caracteres especiais)
        numero_formatado = self._formatar_numero(numero)

        payload = {
            "number": numero_formatado,
            "text": mensagem
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                return {
                    "sucesso": response.status_code == 200 or response.status_code == 201,
                    "status_code": response.status_code,
                    "response": response.json() if response.text else {}
                }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e)
                }

    def _formatar_numero(self, numero: str) -> str:
        """Remove caracteres especiais do número."""
        # Remove tudo que não é dígito
        numero_limpo = "".join(filter(str.isdigit, numero))

        # Se não tem código do país, adiciona 55 (Brasil)
        if len(numero_limpo) <= 11:
            numero_limpo = "55" + numero_limpo

        return numero_limpo

    def extrair_dados_webhook(self, payload: dict) -> dict:
        """Extrai dados relevantes do webhook da Evolution API."""
        try:
            # Estrutura do webhook da Evolution API
            data = payload.get("data", {})

            # Extrai informações da mensagem
            message = data.get("message", {})
            key = data.get("key", {})

            # Número do remetente
            remote_jid = key.get("remoteJid", "")
            numero = remote_jid.replace("@s.whatsapp.net", "").replace("@g.us", "")

            # Texto da mensagem
            texto = ""
            if "conversation" in message:
                texto = message["conversation"]
            elif "extendedTextMessage" in message:
                texto = message["extendedTextMessage"].get("text", "")

            # Verifica se é mensagem de grupo
            is_group = "@g.us" in remote_jid

            # Verifica se é mensagem enviada por mim (para ignorar)
            from_me = key.get("fromMe", False)

            return {
                "numero": numero,
                "texto": texto.strip(),
                "is_group": is_group,
                "from_me": from_me,
                "raw": payload
            }
        except Exception as e:
            return {
                "erro": str(e),
                "raw": payload
            }


# Instância global
whatsapp_client = WhatsAppClient()
