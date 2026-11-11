"""Arquitetura B — workflow determinístico.

O fluxo está escrito no código. O modelo só faz duas tarefas pequenas:
classificar a pergunta e redigir a resposta.

    pergunta ──► classificar ──► tema?
                                   ├── "elegibilidade" ──► escalar (sem chamar o modelo)
                                   └── "rh" | "ti" | "beneficios"
                                          ──► buscar(tema, pergunta) ──► [ modelo + 3 documentos ] ──► resposta

Quem decide o próximo passo é o CÓDIGO, não o modelo.
"""
from comum import modelo
from comum.resultado import Resultado
from ferramentas import buscar, formatar
from politica_de_resposta import FORMATO_JSON, REGRAS

CATEGORIAS = ("rh", "ti", "beneficios", "elegibilidade")


PROMPT_CLASSIFICADOR = """Você classifica perguntas de colaboradores da Aurora Tecnologia em uma categoria.

Categorias:
- rh: férias, licenças, jornada, banco de horas, trabalho remoto, integração de novos colaboradores
- ti: notebook e equipamentos, senhas e acesso, VPN, instalação de software
- beneficios: plano de saúde, vale-refeição, auxílio-creche (valores, prazos, regras)
- elegibilidade: a pessoa pergunta se ELA tem direito a um benefício específico

Responda somente com o nome da categoria, em minúsculas e sem pontuação."""


def classificar(pergunta: str) -> str:
    resposta = modelo.chamar([modelo.mensagem_do_usuario(pergunta)],
                             sistema=PROMPT_CLASSIFICADOR, max_tokens=10)
    categoria = resposta.texto.strip().lower().strip(".\"' ")
    return categoria if categoria in CATEGORIAS else "elegibilidade"


def resolver(pergunta: str) -> Resultado:
    categoria = classificar(pergunta)

    if categoria == "elegibilidade":
        return Resultado("escalar", [], "Sua pergunta depende de análise individual. O RH vai avaliar o seu caso.")

    docs = buscar(categoria, pergunta)
    if not docs:
        return Resultado("nao_sei", [], "Não encontrei essa informação nos documentos.")

    documentos = "\n\n".join(formatar(doc) for doc in docs)
    sistema = f"{REGRAS}\n\n{FORMATO_JSON}\n\nDocumentos disponíveis:\n\n{documentos}"
    resposta = modelo.chamar([modelo.mensagem_do_usuario(pergunta)], sistema=sistema)
    return Resultado.de_json(resposta.texto)
