from datetime import datetime
from .cortes_manager import cortes_manager


def processar_comando(texto: str) -> str:
    texto = texto.lower().strip()
    partes = texto.split()

    if not partes:
        return cmd_ajuda()

    comando = partes[0]
    args = partes[1:] if len(partes) > 1 else []

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
        "lista": lambda: cmd_lista(args),
        "espessura": lambda: cmd_espessura(args),
        "opd": lambda: cmd_opd(args),
        "buscar": lambda: cmd_buscar(args),
        "recarregar": cmd_recarregar,
        "ajuda": cmd_ajuda,
        "help": cmd_ajuda,
        "menu": cmd_ajuda,
    }

    if comando in comandos:
        func = comandos[comando]
        if callable(func):
            return func() if comando in ["status", "pendentes", "concluidos", "recarregar", "ajuda", "help", "menu"] else func()
        return func
    else:
        return cmd_ajuda()


def cmd_status() -> str:
    status = cortes_manager.get_status_geral()
    msg = f"""*STATUS DOS CORTES*

Total: {status["total"]}
Concluidos: {status["concluidos"]}
Pendentes: {status["pendentes"]}

_Digite *pendentes* para ver detalhes._"""
    return msg


def cmd_pendentes() -> str:
    pendentes = cortes_manager.get_pendentes(15)
    if not pendentes:
        return "Nenhum corte pendente!"

    msg = f"*CORTES PENDENTES ({len(pendentes)})*
"
    for corte in pendentes:
        msg += f"
*{corte['numero']}* - Lista {corte['lista_corte']} - {corte['espessura']}mm"
        if corte["tempo_corte"]:
            msg += f" - {corte['tempo_corte']}"
        if corte["opd"]:
            msg += f"
   OPD: {corte['opd']}"

    msg += "

_Para concluir:_ *concluir <numero>*"
    return msg


def cmd_concluidos() -> str:
    concluidos = cortes_manager.get_concluidos(10)
    if not concluidos:
        return "Nenhum corte concluido ainda."

    msg = f"*CORTES CONCLUIDOS (ultimos {len(concluidos)})*
"
    for corte in concluidos:
        msg += f"
*{corte['numero']}* - Lista {corte['lista_corte']} - Corte: {corte['data_corte']}"

    return msg


def cmd_concluir(args: list) -> str:
    if not args:
        return "Informe o numero do corte.

_Exemplo:_ *concluir 4835*"

    numero = args[0]
    resultado = cortes_manager.concluir_corte(numero)

    if not resultado["sucesso"]:
        return f"Erro: {resultado['erro']}"

    corte = resultado["corte"]
    return f"""Corte *{corte['numero']}* marcado como CONCLUIDO!

Lista: {corte['lista_corte']}
Espessura: {corte['espessura']}mm
Data: {corte['data_corte']}"""


def cmd_detalhe(args: list) -> str:
    if not args:
        return "Informe o numero do corte.

_Exemplo:_ *detalhe 4835*"

    numero = args[0]
    corte = cortes_manager.get_detalhe(numero)

    if not corte:
        return f"Corte *{numero}* nao encontrado."

    status = "CONCLUIDO" if corte["data_corte"] else "PENDENTE"

    return f"""*DETALHES DO CORTE*

Numero: {corte['numero']}
Lista: {corte['lista_corte']}
Espessura: {corte['espessura']}mm
Tempo: {corte['tempo_corte']}
OPD: {corte['opd']}
Entrega: {corte['data_entrega']}
Status: {status}
Data Corte: {corte['data_corte'] or '-'}"""


def cmd_lista(args: list) -> str:
    if not args:
        return "Informe o numero da lista.

_Exemplo:_ *lista 219*"

    lista = args[0]
    cortes = cortes_manager.get_por_lista(lista)

    if not cortes:
        return f"Nenhum corte encontrado para lista *{lista}*."

    pendentes = [c for c in cortes if not c["data_corte"]]
    concluidos = [c for c in cortes if c["data_corte"]]

    msg = f"*LISTA {lista}*
"
    msg += f"Total: {len(cortes)} | Pendentes: {len(pendentes)} | Concluidos: {len(concluidos)}
"

    if pendentes:
        msg += "
*Pendentes:*"
        for c in pendentes[:10]:
            msg += f"
- {c['numero']} ({c['espessura']}mm)"

    return msg


def cmd_espessura(args: list) -> str:
    if not args:
        return "Informe a espessura.

_Exemplo:_ *espessura 6.35*"

    espessura = args[0]
    cortes = cortes_manager.get_por_espessura(espessura)

    if not cortes:
        return f"Nenhum corte pendente com espessura *{espessura}*."

    msg = f"*PENDENTES - {espessura}mm ({len(cortes)})*
"
    for c in cortes[:15]:
        msg += f"
*{c['numero']}* - Lista {c['lista_corte']}"

    return msg


def cmd_opd(args: list) -> str:
    if not args:
        return "Informe a OPD.

_Exemplo:_ *opd 290*"

    opd = args[0]
    cortes = cortes_manager.get_por_opd(opd)

    if not cortes:
        return f"Nenhum corte encontrado para OPD *{opd}*."

    pendentes = [c for c in cortes if not c["data_corte"]]
    concluidos = [c for c in cortes if c["data_corte"]]

    msg = f"*OPD {opd}*
"
    msg += f"Total: {len(cortes)} | Pendentes: {len(pendentes)} | Concluidos: {len(concluidos)}
"

    if pendentes:
        msg += "
*Pendentes:*"
        for c in pendentes[:10]:
            msg += f"
- {c['numero']} ({c['espessura']}mm)"

    return msg


def cmd_buscar(args: list) -> str:
    if not args:
        return "Informe o termo de busca.

_Exemplo:_ *buscar 4835*"

    termo = " ".join(args)
    resultados = cortes_manager.buscar(termo)

    if not resultados:
        return f"Nenhum resultado para *{termo}*."

    msg = f"*RESULTADOS ({len(resultados)})*
"
    for c in resultados:
        status = "OK" if c["data_corte"] else "PEND"
        msg += f"
[{status}] *{c['numero']}* - Lista {c['lista_corte']}"

    return msg


def cmd_recarregar() -> str:
    cortes_manager.recarregar()
    status = cortes_manager.get_status_geral()
    return f"""Planilha recarregada!

Total: {status['total']}
Pendentes: {status['pendentes']}
Concluidos: {status['concluidos']}"""


def cmd_ajuda() -> str:
    return """*COMANDOS DISPONIVEIS*

*status* - Resumo geral
*pendentes* - Lista pendentes
*concluidos* - Lista concluidos
*concluir <num>* - Marca como feito
*detalhe <num>* - Detalhes do corte
*lista <num>* - Cortes de uma lista
*espessura <mm>* - Filtra por espessura
*opd <num>* - Cortes de uma OPD
*buscar <termo>* - Busca geral
*recarregar* - Atualiza planilha

_Exemplo:_ *concluir 4835*"""
