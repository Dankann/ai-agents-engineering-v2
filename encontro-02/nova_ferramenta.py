"""TODO 4 — Construir do zero: consultar_rede_credenciada.     (CONTRATO E IMPLEMENTAÇÃO)

Nas ferramentas 1 a 5, a implementação veio pronta e vocês escreveram o contrato.
Aqui não tem nada pronto: vocês escrevem as duas coisas.

O pedido do time de Benefícios
------------------------------
"Todo dia alguém pergunta se tal hospital ou laboratório atende pelo plano. A resposta
está na nossa planilha da rede credenciada, no Google Sheets. Queremos que o assistente
consulte a planilha."

O sistema: a planilha
---------------------
    SHEETS.ler("planilha-rede-credenciada", "prestadores")

devolve o mesmo formato da API do Google Sheets (spreadsheets.values.get):

    {"spreadsheetId": "planilha-rede-credenciada",
     "range": "prestadores!A1:L31",
     "majorDimension": "ROWS",
     "values": [
        ["prestador", "tipo", "especialidades", "cidade", "uf", "bairro", "telefone",
         "atende_24h", "situacao", "codigo_operadora", "valor_negociado_consulta",
         "observacao_interna"],                                            <- cabeçalho
        ["Hospital Jacarandá Paulista", "Hospital", "clínica geral; ...", "São Paulo", ...],
        ...
     ]}

Tudo vem como texto, e a planilha é mantida à mão desde 2021. Olhem os dados antes
de escrever qualquer linha:

    python encontro-02/nova_ferramenta.py          (a partir da raiz: imprime a planilha inteira)

Passo a passo
-------------
  4a. IMPLEMENTAÇÃO: escrevam consultar_rede_credenciada(). Decidam os parâmetros.
      Devolvam um dicionário com a lista de prestadores em "resultados" (um dicionário
      por prestador). Chaves fora de "resultados" também podem voltar ao modelo,
      se o contrato declarar (ex.: a fonte).
  4b. CONTRATO: preencham CONTRATO (descrição, schema, saída), como nos TODOs 1 a 3.
      Os parâmetros do schema precisam bater com os da função.
  4c. TESTE: assim que CONTRATO["parametros"] deixar de ser None, a ferramenta entra
      no catálogo do agente sozinha. Os casos c16 e c17 dependem dela:

          python encontro-02/rodar.py --casos c16 c17 --detalhe

Perguntas para decidir
----------------------
  - Que parâmetros o modelo precisa para chegar ao prestador certo? Quais valores aceitar?
  - "Campinas", "campinas" e "CAMPINAS " são a mesma cidade. Quem resolve isso: o modelo
    ou o código?
  - A planilha tem prestadores descredenciados e em negociação. O modelo deveria vê-los?
  - São Paulo tem mais de dez prestadores. Quantos voltam para o contexto?
  - Quais colunas nunca deveriam entrar no contexto? (O placar tem uma coluna para isso.)
  - Como o agente cita a planilha como fonte?
  - E erros: cidade sem prestador? Tipo que não existe?
"""
import unicodedata

from ferramentas import ErroDeFerramenta   # para devolver erros legíveis ao modelo (veja ferramentas.py)
from sistemas import PlanilhaGoogle

SHEETS = PlanilhaGoogle()
PLANILHA_ID = "planilha-rede-credenciada"
ABA = "prestadores"


def normalizar(texto: str) -> str:
    """'  São Paulo ' -> 'sao paulo'. Minúsculas, sem acento, sem espaço nas pontas."""
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.lower().split())


# ======================================================================
# TODO 4a — a implementação
#
# Troquem a assinatura pelos parâmetros que vocês decidirem (com tipos e valores
# padrão) e escrevam o corpo. Esqueleto sugerido:
#   1. ler a planilha com SHEETS.ler(PLANILHA_ID, ABA)
#   2. transformar cada linha num dicionário (cabeçalho -> valor)
#   3. filtrar (normalizar() ajuda)
#   4. devolver {"resultados": [...], ...}
# ======================================================================
TIPOS = {"hospital": "hospital", "laboratorio": "laboratorio", "clinica": "clinica",
         "pronto_socorro": "pronto-socorro"}
MAXIMO = 5


def _linhas_como_dicts() -> list:
    cabecalho, *linhas = SHEETS.ler(PLANILHA_ID, ABA)["values"]
    return [dict(zip(cabecalho, linha + [""] * (len(cabecalho) - len(linha)))) for linha in linhas]


def consultar_rede_credenciada(cidade: str, tipo: str | None = None, especialidade: str | None = None,
                               apenas_24h: bool = False) -> dict:
    """Prestadores ATIVOS da rede na cidade, filtrados por tipo, especialidade e atendimento 24h."""
    if tipo is not None and tipo not in TIPOS:
        raise ErroDeFerramenta("tipo_invalido", "'tipo' não é um valor aceito.", recebido=tipo,
                               aceitos=list(TIPOS), como_corrigir="repita com um dos tipos aceitos ou sem tipo")
    linhas = _linhas_como_dicts()
    na_cidade = [l for l in linhas if normalizar(l["cidade"]) == normalizar(cidade)]
    if not na_cidade:
        grafias = {}
        for l in linhas:
            if normalizar(l["situacao"]) == "ativo":
                grafias.setdefault(normalizar(l["cidade"]), []).append(l["cidade"].strip().title())
        cidades = sorted(max(v) for v in grafias.values())
        raise ErroDeFerramenta("cidade_sem_prestador", "A rede não tem prestador nessa cidade.", recebido=cidade,
                               aceitos=cidades, recuperavel=False,
                               como_corrigir="diga ao colaborador que a rede não cobre essa cidade")

    achados = [l for l in na_cidade if normalizar(l["situacao"]) == "ativo"]
    if tipo:
        achados = [l for l in achados if normalizar(l["tipo"]) == TIPOS[tipo]]
    if especialidade:
        achados = [l for l in achados if normalizar(especialidade) in normalizar(l["especialidades"])]
    if apenas_24h:
        achados = [l for l in achados if normalizar(l["atende_24h"]) == "sim"]

    resultados = [{
        "prestador": l["prestador"], "tipo": normalizar(l["tipo"]), "especialidades": l["especialidades"],
        "cidade": l["cidade"].strip().title(), "uf": l["uf"], "bairro": l["bairro"], "telefone": l["telefone"],
        "atende_24h": normalizar(l["atende_24h"]) == "sim",
    } for l in achados[:MAXIMO]]
    registro = {"id": PLANILHA_ID, "resultados": resultados}
    if len(achados) > MAXIMO:
        registro["aviso"] = f"Há {len(achados)} prestadores; mostrando {MAXIMO}. Refine por tipo ou especialidade."
    return registro


# ======================================================================
# TODO 4b — o contrato (mesmo formato de contratos.py)
# ======================================================================
CONTRATO = {
    "descricao": (
        "Consulta a planilha da rede credenciada do plano de saúde da Aurora: hospitais, laboratórios, "
        "clínicas e prontos-socorros que atendem pelo plano, por cidade. Devolve só prestadores ativos, com "
        "nome, tipo, especialidades, endereço, telefone e se atende 24 horas. O id devolvido "
        "(planilha-rede-credenciada) é a fonte a citar. Use quando o colaborador perguntar onde ou se um tipo "
        "de prestador atende pelo plano. Não use para regras do plano (coparticipação, carência, valores): "
        "isso é consultar_regra_beneficio. Se a cidade não tiver prestador, a ferramenta devolve as cidades "
        "atendidas."
    ),
    "parametros": {
        "type": "object",
        "properties": {
            "cidade": {"type": "string", "maxLength": 60,
                       "description": "A cidade do colaborador, como ele escreveu. Ex.: Campinas."},
            "tipo": {"type": "string", "enum": ["hospital", "laboratorio", "clinica", "pronto_socorro"],
                     "description": "Filtra pelo tipo de prestador. Omita para todos os tipos."},
            "especialidade": {"type": "string", "maxLength": 60,
                              "description": "Filtra por especialidade ou exame. Ex.: pediatria, exames de sangue."},
            "apenas_24h": {"type": "boolean",
                           "description": "true para só prestadores que atendem 24 horas. Padrão: false."},
        },
        "required": ["cidade"],
        "additionalProperties": False,
    },
    "saida": ["id", "prestador", "tipo", "especialidades", "cidade", "uf", "bairro", "telefone", "atende_24h"],
}


NOME = "consultar_rede_credenciada"


if __name__ == "__main__":   # olhar os dados antes de escrever a ferramenta
    for linha in SHEETS.ler(PLANILHA_ID, ABA)["values"]:
        print(linha)
