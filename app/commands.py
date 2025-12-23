from datetime import datetime
from .cortes_manager import cortes_manager


def formatar_data(data_str: str) -> str:
    """Converte data de YYYY-MM-DD para DD/MM/YYYY."""
    if not data_str:
        return "-"
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d")
        return data.strftime("%d/%m/%Y")
    except:
        return data_str


def get_emoji_prioridade(prioridade: str) -> str:
    """Retorna emoji baseado na prioridade."""
    emojis = {
        "alta": "🔴",
        "media": "🟡",
        "baixa": "🟢"
    }
    return emojis.get(prioridade.lower(), "⚪")


def processar_comando(texto: str) -> str:
    """Processa o comando recebido e retorna a resposta."""
    texto = texto.lower().strip()
    partes = texto.split()

    if not partes:
        return cmd_ajuda()

    comando = partes[0]
    args = partes[1:] if len(partes) > 1 else []

    # Mapeamento de comandos
    comandos = {
        "status": cmd_status,
        "pendentes": cmd_pendentes,
        "pendente": cmd_pendentes,
        "concluidos": cmd_concluidos,
        "concluido": cmd_concluidos,
        "concluir": lambda: cmd_concluir(args),
        "finalizar": lambda: cmd_concluir(args),
        "detalhe": lambda: cmd_detalhe(args),
        "detalhes": lambda: cmd_detalhe(args),
        "prioridade": lambda: cmd_prioridade(args),
        "recarregar": cmd_recarregar,
        "ajuda": cmd_ajuda,
        "help": cmd_ajuda,
        "menu": cmd_ajuda,
    }

    if comando in comandos:
        func = comandos[comando]
        if callable(func):
            return func() if not args or comando in ["status", "pendentes", "concluidos", "recarregar", "ajuda", "help", "menu"] else func()
        return func
    else:
        return cmd_ajuda()


def cmd_status() -> str:
    """Retorna o status geral dos cortes."""
    status = cortes_manager.get_status_geral()

    msg = f"""📊 *Status dos Cortes*

✅ Concluídos: {status['concluidos']}
⏳ Pendentes: {status['pendentes']}
📋 Total: {status['total']}

*Pendentes por prioridade:*
🔴 Alta: {status['prioridade_alta']}
🟡 Média: {status['prioridade_media']}
🟢 Baixa: {status['prioridade_baixa']}

_Digite *pendentes* para ver detalhes._"""

    return msg


def cmd_pendentes() -> str:
    """Lista os cortes pendentes."""
    pendentes = cortes_manager.get_pendentes()

    if not pendentes:
        return "✅ *Parabéns!* Não há cortes pendentes."

    msg = f"⏳ *Cortes Pendentes ({len(pendentes)})*\n"

    for corte in pendentes:
        emoji = get_emoji_prioridade(corte["prioridade"])
        msg += f"""
{emoji} *{corte['codigo']}* - {corte['descricao']}
   📅 Previsto: {formatar_data(corte['data_prevista'])}
   👤 Responsável: {corte['responsavel']}
"""

    msg += "\n_Para concluir, digite:_ *concluir <código>*"
    return msg


def cmd_concluidos() -> str:
    """Lista os cortes concluídos."""
    concluidos = cortes_manager.get_concluidos()

    if not concluidos:
        return "📋 Nenhum corte concluído ainda."

    msg = f"✅ *Cortes Concluídos ({len(concluidos)})*\n"

    for corte in concluidos:
        msg += f"""
• *{corte['codigo']}* - {corte['descricao']}
   📅 Concluído: {formatar_data(corte['data_conclusao'])}
   👤 Responsável: {corte['responsavel']}
"""

    return msg


def cmd_concluir(args: list) -> str:
    """Marca um corte como concluído."""
    if not args:
        return "⚠️ Informe o código do corte.\n\n_Exemplo:_ *concluir CRT-001*"

    codigo = args[0].upper()
    resultado = cortes_manager.concluir_corte(codigo)

    if not resultado["sucesso"]:
        return f"❌ {resultado['erro']}"

    corte = resultado["corte"]
    return f"""✅ Corte *{corte['codigo']}* marcado como concluído!

📝 {corte['descricao']}
👤 Responsável: {corte['responsavel']}
📅 Concluído em: {formatar_data(corte['data_conclusao'])}"""


def cmd_detalhe(args: list) -> str:
    """Mostra detalhes de um corte específico."""
    if not args:
        return "⚠️ Informe o código do corte.\n\n_Exemplo:_ *detalhe CRT-001*"

    codigo = args[0].upper()
    corte = cortes_manager.get_detalhe(codigo)

    if not corte:
        return f"❌ Corte *{codigo}* não encontrado."

    emoji = get_emoji_prioridade(corte["prioridade"])
    status_emoji = "✅" if corte["status"] == "concluido" else "⏳"

    msg = f"""📋 *Detalhes do Corte*

*Código:* {corte['codigo']}
*Descrição:* {corte['descricao']}
*Status:* {status_emoji} {corte['status'].capitalize()}
*Prioridade:* {emoji} {corte['prioridade'].capitalize()}
*Responsável:* {corte['responsavel']}
*Data Prevista:* {formatar_data(corte['data_prevista'])}
*Data Conclusão:* {formatar_data(corte['data_conclusao'])}"""

    return msg


def cmd_prioridade(args: list) -> str:
    """Lista cortes por prioridade."""
    if not args:
        return "⚠️ Informe a prioridade: *alta*, *media* ou *baixa*\n\n_Exemplo:_ *prioridade alta*"

    prioridade = args[0].lower()
    if prioridade not in ["alta", "media", "média", "baixa"]:
        return "⚠️ Prioridade inválida. Use: *alta*, *media* ou *baixa*"

    if prioridade == "média":
        prioridade = "media"

    cortes = cortes_manager.get_por_prioridade(prioridade)
    emoji = get_emoji_prioridade(prioridade)

    if not cortes:
        return f"{emoji} Nenhum corte pendente com prioridade *{prioridade}*."

    msg = f"{emoji} *Cortes Pendentes - Prioridade {prioridade.capitalize()} ({len(cortes)})*\n"

    for corte in cortes:
        msg += f"""
• *{corte['codigo']}* - {corte['descricao']}
   📅 Previsto: {formatar_data(corte['data_prevista'])}
   👤 {corte['responsavel']}
"""

    return msg


def cmd_recarregar() -> str:
    """Recarrega a planilha do disco."""
    cortes_manager.recarregar()
    status = cortes_manager.get_status_geral()
    return f"""🔄 Planilha recarregada com sucesso!

📋 Total de cortes: {status['total']}
⏳ Pendentes: {status['pendentes']}
✅ Concluídos: {status['concluidos']}"""


def cmd_ajuda() -> str:
    """Retorna a lista de comandos disponíveis."""
    return """🤖 *Agente de Cortes - Comandos*

📊 *status* - Resumo geral dos cortes
⏳ *pendentes* - Lista cortes pendentes
✅ *concluidos* - Lista cortes concluídos
✔️ *concluir <código>* - Marca corte como concluído
📋 *detalhe <código>* - Detalhes de um corte
🎯 *prioridade <alta/media/baixa>* - Filtra por prioridade
🔄 *recarregar* - Atualiza lista do arquivo

_Exemplo:_ *concluir CRT-001*"""
