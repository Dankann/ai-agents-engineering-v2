"""Verifica se o ambiente está pronto para a disciplina.

    python setup/verificar_ambiente.py

Roda antes da primeira aula (o "encontro zero"). Faz uma chamada mínima ao
modelo, que custa uma fração de centavo.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


def passo(ok: bool, mensagem: str) -> None:
    print(("  [ok]   " if ok else "  [FALHA] ") + mensagem)
    if not ok:
        sys.exit(1)


print("Verificando o ambiente...\n")
passo(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]} (precisa ser 3.10 ou mais novo)")

try:
    import dotenv  # noqa: F401
except ImportError:
    passo(False, "falta instalar dependências. Rode: pip install -r requirements.txt")

passo((RAIZ / ".env").exists(), "arquivo .env encontrado (copie o .env.example e preencha)")

import os  # noqa: E402

from comum import medidor, modelo  # noqa: E402

if modelo.PROVEDOR == "anthropic":
    try:
        import anthropic  # noqa: F401
    except ImportError:
        passo(False, "falta a biblioteca anthropic. Rode: pip install -r requirements.txt")
    passo(True, "bibliotecas instaladas")
    chave = os.getenv("ANTHROPIC_API_KEY", "")
    passo(chave.startswith("sk-"), "ANTHROPIC_API_KEY preenchida no .env")

try:
    medidor.zerar()
    resposta = modelo.chamar([modelo.mensagem_do_usuario("Responda apenas com a palavra: pronto")],
                             max_tokens=10)
    m = medidor.atual()
    passo(True, f"modelo respondeu: '{resposta.texto.strip()}' "
                f"({m.tokens_entrada} tokens de entrada, {m.tokens_saida} de saída, US$ {m.custo_usd:.6f})")
except Exception as erro:
    passo(False, f"chamada ao modelo falhou: {type(erro).__name__}: {erro}")

if modelo.PROVEDOR == "fake":
    print("\nTudo instalado, mas você está no modo fake (respostas simuladas).")
    print("Para a aula, troque PROVEDOR=anthropic no .env.")
else:
    print(f"\nTudo pronto. Provedor: {modelo.PROVEDOR} · modelo: {modelo.MODELO}")
