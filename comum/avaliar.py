"""Compara um Resultado com o gabarito do caso.

A nota olha só o desfecho e as fontes, não o texto da resposta.
Assim a correção é automática, rápida e igual para todo mundo.
(Avaliar o texto com outro modelo, o "LLM-as-judge", é tema do Encontro 5.)
"""
from comum.resultado import Resultado


def avaliar(resultado: Resultado, caso: dict) -> tuple[bool, str]:
    esperado = caso["esperado"]

    if resultado.desfecho == "invalido":
        return False, "saída fora do contrato"

    if resultado.desfecho != esperado["desfecho"]:
        return False, f"desfecho '{resultado.desfecho}', esperado '{esperado['desfecho']}'"

    faltando = [f for f in esperado.get("fontes_obrigatorias", []) if f not in resultado.fontes]
    if faltando:
        return False, "não citou " + ", ".join(faltando)

    return True, "ok"
