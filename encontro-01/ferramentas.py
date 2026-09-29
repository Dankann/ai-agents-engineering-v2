"""Acesso aos documentos de política da Aurora Tecnologia.

Neste encontro as "ferramentas" são funções Python comuns que leem arquivos
da pasta corpus/. No Encontro 2 elas passam a ser servidas via MCP.

    carregar_corpus()          todos os documentos
    buscar(tema, consulta)     até 3 documentos mais parecidos com a consulta
    formatar(documento)        o documento como texto para colocar no prompt
"""
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

PASTA_CORPUS = Path(__file__).parent / "corpus"
TEMAS = ("rh", "ti", "beneficios")


@dataclass
class Documento:
    id: str
    titulo: str
    tema: str
    dono: str
    atualizado_em: str
    texto: str


def _ler(caminho: Path) -> Documento:
    bruto = caminho.read_text(encoding="utf-8")
    _, cabecalho, texto = bruto.split("---", 2)
    campos = dict(linha.split(":", 1) for linha in cabecalho.strip().splitlines())
    campos = {chave.strip(): valor.strip() for chave, valor in campos.items()}
    return Documento(texto=texto.strip(), **campos)


_cache: list | None = None


def carregar_corpus() -> list:
    global _cache
    if _cache is None:
        _cache = [_ler(c) for c in sorted(PASTA_CORPUS.glob("*.md"))]
    return _cache


def formatar(doc: Documento) -> str:
    return (f'<documento id="{doc.id}" tema="{doc.tema}" dono="{doc.dono}" '
            f'atualizado_em="{doc.atualizado_em}">\n# {doc.titulo}\n\n{doc.texto}\n</documento>')


# ------------------------------------------------------------ busca léxica
# Busca simples por palavras, de propósito. Busca por significado
# (embeddings e banco vetorial) é o tema do Encontro 3.

_PALAVRAS_VAZIAS = set("""
a o as os um uma uns umas de do da dos das no na nos nas em para por com sem
que qual quais quando como onde e ou se eu meu minha meus minhas me mim voce
ao aos ate mais muito ja nao sim ser ter tem tenho posso pode vou vai esta estou
isso este essa esse aqui hoje sobre fazer faco alguma algum coisa
""".split())


def _radicais(texto: str) -> set:
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    palavras = re.findall(r"[a-z0-9]+", sem_acento)
    return {p[:5] for p in palavras if p not in _PALAVRAS_VAZIAS and len(p) > 2}


def buscar(tema: str, consulta: str, k: int = 3) -> list:
    """Devolve até k documentos do tema ('rh', 'ti', 'beneficios' ou 'todos')."""
    alvo = _radicais(consulta)
    pontuados = []
    for doc in carregar_corpus():
        if tema != "todos" and doc.tema != tema:
            continue
        pontos = len(alvo & _radicais(doc.texto)) + 2 * len(alvo & _radicais(doc.titulo))
        if pontos > 0:
            pontuados.append((pontos, doc))
    pontuados.sort(key=lambda par: -par[0])
    return [doc for _, doc in pontuados[:k]]


def buscar_formatado(tema: str, consulta: str) -> str:
    """Mesma busca, já em texto, para devolver ao modelo como resultado de ferramenta."""
    docs = buscar(tema, consulta)
    if not docs:
        return "Nenhum documento encontrado para essa busca."
    return "\n\n".join(formatar(d) for d in docs)
