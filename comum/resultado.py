"""O contrato de saída: toda arquitetura devolve um Resultado.

    desfecho  "responder" | "escalar" | "nao_sei"
    fontes    ids dos documentos que sustentam a resposta
    resposta  texto curto para o colaborador

Se o modelo devolver algo fora desse formato, o desfecho vira "invalido"
e a execução conta como erro. Respeitar o contrato faz parte da nota.
"""
import json
from dataclasses import dataclass, field

DESFECHOS = ("responder", "escalar", "nao_sei")


@dataclass
class Resultado:
    desfecho: str
    fontes: list = field(default_factory=list)
    resposta: str = ""

    @classmethod
    def de_json(cls, texto: str) -> "Resultado":
        """Lê o JSON devolvido pelo modelo. Tolera texto antes ou depois das chaves."""
        inicio, fim = texto.find("{"), texto.rfind("}")
        if inicio == -1 or fim <= inicio:
            return cls("invalido", [], texto.strip())
        try:
            dados = json.loads(texto[inicio : fim + 1])
        except json.JSONDecodeError:
            return cls("invalido", [], texto.strip())
        return cls.de_dict(dados)

    @classmethod
    def de_dict(cls, dados: dict) -> "Resultado":
        desfecho = str(dados.get("desfecho", "")).strip().lower()
        if desfecho not in DESFECHOS:
            desfecho = "invalido"
        fontes = dados.get("fontes") or []
        if not isinstance(fontes, list):
            fontes = [fontes]
        return cls(desfecho, [str(f) for f in fontes], str(dados.get("resposta", "")))
