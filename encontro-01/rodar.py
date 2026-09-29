"""Roda as arquiteturas sobre os 10 casos, mede e imprime o placar.

Exemplos (a partir da raiz do repositório):

    python encontro-01/rodar.py --arq a              só a arquitetura A
    python encontro-01/rodar.py --arq a b c          as três
    python encontro-01/rodar.py --arq c --repeticoes 3   C três vezes (variância)
    python encontro-01/rodar.py --arq b --casos c05 c06 --detalhe
    python encontro-01/rodar.py --de-csv resultados/arquivo.csv   reimprime um placar salvo

Cada execução também é salva em encontro-01/resultados/ como CSV.
"""
import argparse
import csv
import importlib
import json
import math
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ))

from comum import medidor, modelo  # noqa: E402
from comum.avaliar import avaliar  # noqa: E402

NOMES = {"a": "A · Prompt único", "b": "B · Workflow", "c": "C · Agente em loop"}
CAMPOS = ["arquitetura", "caso", "repeticao", "acerto", "motivo", "desfecho", "fontes",
          "chamadas", "tokens_entrada", "tokens_saida", "custo_usd", "segundos", "resposta"]


def carregar_casos(filtro: list | None) -> list:
    casos = json.loads((AQUI / "casos.json").read_text(encoding="utf-8"))
    return [c for c in casos if not filtro or c["id"] in filtro]


def executar_um(arquitetura, letra: str, caso: dict, repeticao: int) -> dict:
    medicao = medidor.zerar()
    inicio = time.perf_counter()
    try:
        resultado = arquitetura.resolver(caso["pergunta"])
        acerto, motivo = avaliar(resultado, caso)
        desfecho, fontes, resposta = resultado.desfecho, resultado.fontes, resultado.resposta
    except NotImplementedError:
        raise
    except Exception as erro:  # erro de API, de código etc. conta como erro no placar
        acerto, motivo = False, f"erro: {type(erro).__name__}: {erro}"
        desfecho, fontes, resposta = "erro", [], ""
    return {
        "arquitetura": letra, "caso": caso["id"], "repeticao": repeticao,
        "acerto": acerto, "motivo": motivo, "desfecho": desfecho, "fontes": " ".join(fontes),
        "chamadas": medicao.chamadas, "tokens_entrada": medicao.tokens_entrada,
        "tokens_saida": medicao.tokens_saida, "custo_usd": medicao.custo_usd,
        "segundos": time.perf_counter() - inicio, "resposta": resposta,
    }


def percentil(valores: list, p: float) -> float:
    ordenados = sorted(valores)
    return ordenados[max(0, math.ceil(p * len(ordenados)) - 1)]


def imprimir_placar(linhas: list) -> None:
    letras = [l for l in "abc" if any(x["arquitetura"] == l for x in linhas)]
    casos = sorted({x["caso"] for x in linhas})
    repeticoes = max(int(x["repeticao"]) for x in linhas)

    # 1) caso a caso: onde cada arquitetura acertou ou errou
    print("\nCaso a caso" + (f" (acertos em {repeticoes} repetições)" if repeticoes > 1 else ""))
    print("caso  " + "".join(f"{NOMES[l]:<34}" for l in letras))
    for caso in casos:
        celulas = []
        for l in letras:
            rodadas = [x for x in linhas if x["arquitetura"] == l and x["caso"] == caso]
            acertos = sum(1 for x in rodadas if x["acerto"])
            if repeticoes == 1:
                celulas.append("ok" if acertos else "x " + rodadas[0]["motivo"][:30])
            else:
                celulas.append(f"{acertos}/{len(rodadas)}")
        print(f"{caso:<6}" + "".join(f"{c:<34}" for c in celulas))

    # 2) o placar que vai para o quadro
    print(f"\nPlacar ({len(casos)} casos" + (f", média de {repeticoes} repetições)" if repeticoes > 1 else ")"))
    cabecalho = f"{'Arquitetura':<22}{'Acertos':>9}{'Custo total':>14}{'p50 (s)':>9}{'p95 (s)':>9}{'Custo/acerto':>15}"
    if repeticoes > 1:
        cabecalho += f"{'Casos que variaram':>20}"
    print(cabecalho)
    print("-" * len(cabecalho))
    for l in letras:
        dela = [x for x in linhas if x["arquitetura"] == l]
        acertos = sum(1 for x in dela if x["acerto"])
        custo = sum(float(x["custo_usd"]) for x in dela)
        tempos = [float(x["segundos"]) for x in dela]
        por_acerto = f"US$ {custo / acertos:.5f}" if acertos else "sem acertos"
        linha = (f"{NOMES[l]:<22}{acertos / repeticoes:>6.1f}/{len(casos):<2}"
                 f"{'US$ ' + format(custo / repeticoes, '.5f'):>14}"
                 f"{statistics.median(tempos):>9.2f}{percentil(tempos, 0.95):>9.2f}{por_acerto:>15}")
        if repeticoes > 1:
            variaram = sum(
                1 for caso in casos
                if len({x["desfecho"] for x in dela if x["caso"] == caso}) > 1
            )
            linha += f"{variaram:>20}"
        print(linha)
    print(f"\nCusto total = média por rodada dos {len(casos)} casos. Custo/acerto = custo total ÷ acertos."
          "\nLatência (p50/p95) = tempo por pergunta, em segundos.")


def salvar_csv(linhas: list, sufixo: str) -> Path:
    pasta = AQUI / "resultados"
    pasta.mkdir(exist_ok=True)
    caminho = pasta / f"execucao_{datetime.now():%Y%m%d_%H%M%S}_{sufixo}.csv"
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def ler_csv(caminho: str) -> list:
    with open(caminho, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    for x in linhas:
        x["acerto"] = x["acerto"] == "True"
    return linhas


def main() -> None:
    parser = argparse.ArgumentParser(description="Hands-on 1: um problema, três arquiteturas.")
    parser.add_argument("--arq", nargs="+", choices=["a", "b", "c"], default=["a", "b", "c"])
    parser.add_argument("--repeticoes", type=int, default=1)
    parser.add_argument("--casos", nargs="+", help="ids dos casos, ex.: c05 c06")
    parser.add_argument("--detalhe", action="store_true", help="mostra desfecho e fontes de cada execução")
    parser.add_argument("--solucao", action="store_true", help="usa a solução do professor para B e C")
    parser.add_argument("--de-csv", help="só reimprime o placar de um CSV salvo")
    args = parser.parse_args()

    if args.de_csv:
        imprimir_placar(ler_csv(args.de_csv))
        return

    if args.solucao:
        pasta = RAIZ / "professor" / "solucao-encontro-01"
        if not pasta.exists():
            sys.exit("A pasta professor/ não existe nesta cópia do repositório.")
        sys.path.insert(0, str(pasta))

    casos = carregar_casos(args.casos)
    print(f"Provedor: {modelo.PROVEDOR} · modelo: {modelo.MODELO} · {len(casos)} casos · "
          f"{args.repeticoes} repetição(ões)")
    if modelo.PROVEDOR == "fake":
        print("ATENÇÃO: modo fake. As respostas são simuladas e o placar não significa nada.")

    linhas = []
    for letra in args.arq:
        arquitetura = importlib.import_module(f"arquitetura_{letra}")
        print(f"\nRodando {NOMES[letra]} ", end="", flush=True)
        try:
            for repeticao in range(1, args.repeticoes + 1):
                for caso in casos:
                    linha = executar_um(arquitetura, letra, caso, repeticao)
                    linhas.append(linha)
                    if not args.detalhe:
                        print("." if linha["acerto"] else "x", end="", flush=True)
                    else:
                        print(f"\n  {caso['id']} r{repeticao}: {linha['desfecho']} [{linha['fontes']}] "
                              f"{linha['chamadas']} chamada(s) · {linha['motivo']}", end="")
        except NotImplementedError as pendente:
            print(f"\n  → ainda tem TODO pendente: {pendente}")
            linhas = [x for x in linhas if x["arquitetura"] != letra]
            continue
        print()

    erros = [x for x in linhas if x["motivo"].startswith("erro:")]
    if erros:
        print(f"\n{len(erros)} execução(ões) com erro. Exemplo: {erros[0]['motivo'][:200]}")

    if linhas:
        imprimir_placar(linhas)
        caminho = salvar_csv(linhas, "".join(args.arq))
        print(f"\nResultados salvos em {caminho.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
