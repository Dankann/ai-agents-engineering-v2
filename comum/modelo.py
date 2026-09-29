"""Único ponto de contato com o provedor do modelo.

Todo o resto do projeto chama só estas funções:

    chamar(mensagens, sistema, ferramentas)  -> Resposta
    mensagem_do_usuario(texto)
    mensagem_do_assistente(resposta)
    mensagem_de_resultados([(chamada, texto_do_resultado), ...])

Trocar de provedor significa reescrever apenas este arquivo.

Provedores disponíveis (variável PROVEDOR no .env):
    anthropic  chamadas reais (precisa de ANTHROPIC_API_KEY)
    fake       respostas simuladas, sem custo. Serve só para testar a instalação.
"""
import os
import re
import time
from dataclasses import dataclass

from comum import medidor

PROVEDOR = os.getenv("PROVEDOR", "anthropic").strip().lower()
MODELO = os.getenv("MODELO", "claude-haiku-4-5-20251001").strip()


@dataclass
class Chamada:
    """Um pedido do modelo para usar uma ferramenta."""
    id: str
    nome: str
    args: dict


@dataclass
class Resposta:
    texto: str        # o que o modelo escreveu
    chamadas: list    # ferramentas que o modelo pediu para usar (lista de Chamada)
    conteudo: list    # a resposta no formato do provedor, para voltar ao histórico


# ---------------------------------------------------------------- interface

def chamar(mensagens: list, sistema: str = "", ferramentas: list | None = None,
           max_tokens: int = 1024) -> Resposta:
    """Envia a conversa ao modelo e devolve a resposta.

    ferramentas: lista de dicts no formato neutro do projeto:
        {"nome": ..., "descricao": ..., "parametros": <JSON Schema>}
    """
    if PROVEDOR == "anthropic":
        return _chamar_anthropic(mensagens, sistema, ferramentas, max_tokens)
    if PROVEDOR == "fake":
        return _chamar_fake(mensagens, sistema, ferramentas)
    raise ValueError(f"PROVEDOR desconhecido no .env: '{PROVEDOR}'. Use 'anthropic' ou 'fake'.")


def mensagem_do_usuario(texto: str) -> dict:
    return {"role": "user", "content": texto}


def mensagem_do_assistente(resposta: Resposta) -> dict:
    return {"role": "assistant", "content": resposta.conteudo}


def mensagem_de_resultados(pares: list) -> dict:
    """Devolve ao modelo o resultado de cada ferramenta que ele pediu."""
    return {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": chamada.id, "content": texto}
            for chamada, texto in pares
        ],
    }


# ---------------------------------------------------------------- anthropic

_cliente = None


def _chamar_anthropic(mensagens, sistema, ferramentas, max_tokens) -> Resposta:
    global _cliente
    import anthropic

    if _cliente is None:
        _cliente = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do ambiente

    pedido = {"model": MODELO, "max_tokens": max_tokens, "messages": mensagens}
    if sistema:
        pedido["system"] = sistema
    if ferramentas:
        pedido["tools"] = [
            {"name": f["nome"], "description": f["descricao"], "input_schema": f["parametros"]}
            for f in ferramentas
        ]
    if os.getenv("TEMPERATURA"):
        pedido["temperature"] = float(os.environ["TEMPERATURA"])

    inicio = time.perf_counter()
    r = _cliente.messages.create(**pedido)
    medidor.registrar(r.usage.input_tokens, r.usage.output_tokens, time.perf_counter() - inicio)

    texto, chamadas, conteudo = [], [], []
    for bloco in r.content:
        if bloco.type == "text":
            texto.append(bloco.text)
            conteudo.append({"type": "text", "text": bloco.text})
        elif bloco.type == "tool_use":
            chamadas.append(Chamada(bloco.id, bloco.name, dict(bloco.input)))
            conteudo.append({"type": "tool_use", "id": bloco.id, "name": bloco.name,
                             "input": dict(bloco.input)})
    return Resposta("".join(texto), chamadas, conteudo)


# ---------------------------------------------------------------- fake

def _texto_plano(sistema: str, mensagens: list) -> str:
    partes = [sistema]
    for m in mensagens:
        if isinstance(m["content"], str):
            partes.append(m["content"])
        else:
            for bloco in m["content"]:
                partes.append(str(bloco.get("text") or bloco.get("content") or bloco.get("input") or ""))
    return "\n".join(partes)


def _chamar_fake(mensagens, sistema, ferramentas) -> Resposta:
    """Simula o modelo sem chamar API nenhuma. Não mede nada real: só testa o encanamento."""
    texto_total = _texto_plano(sistema, mensagens)
    ids = re.findall(r'id="([a-z0-9-]+)"', texto_total)
    medidor.registrar(len(texto_total) // 4, 40, 0.01)

    if ferramentas:
        ja_buscou = any(
            isinstance(m["content"], list) and any(b.get("type") == "tool_result" for b in m["content"])
            for m in mensagens
        )
        if not ja_buscou:
            pergunta = mensagens[0]["content"]
            chamada = Chamada("fake-1", "buscar", {"tema": "todos", "consulta": pergunta})
        else:
            chamada = Chamada("fake-2", "responder", {"desfecho": "responder", "fontes": ids[:1],
                                                      "resposta": "(resposta simulada)"})
        conteudo = [{"type": "tool_use", "id": chamada.id, "name": chamada.nome, "input": chamada.args}]
        return Resposta("", [chamada], conteudo)

    if not ids:  # sem documentos no contexto: provavelmente é o classificador
        return Resposta("rh", [], [{"type": "text", "text": "rh"}])

    texto = '{"desfecho": "responder", "fontes": ["%s"], "resposta": "(resposta simulada)"}' % ids[0]
    return Resposta(texto, [], [{"type": "text", "text": texto}])
