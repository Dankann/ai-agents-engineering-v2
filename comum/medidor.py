"""Mede tokens, chamadas ao modelo e custo de uma execução.

Toda chamada feita por comum/modelo.py é registrada aqui automaticamente.
O rodar.py zera o medidor antes de cada pergunta e lê o total no fim.
"""
import os
from dataclasses import dataclass


def _preco(variavel: str, padrao: str) -> float:
    return float(os.getenv(variavel, padrao))


# Preço em dólares por milhão de tokens. Confira na página de preços do provedor.
PRECO_ENTRADA = _preco("PRECO_ENTRADA_USD_POR_MILHAO", "1.00")
PRECO_SAIDA = _preco("PRECO_SAIDA_USD_POR_MILHAO", "5.00")


@dataclass
class Medicao:
    chamadas: int = 0
    tokens_entrada: int = 0
    tokens_saida: int = 0
    segundos_no_modelo: float = 0.0

    @property
    def custo_usd(self) -> float:
        return (self.tokens_entrada * PRECO_ENTRADA + self.tokens_saida * PRECO_SAIDA) / 1_000_000


_atual = Medicao()


def zerar() -> Medicao:
    global _atual
    _atual = Medicao()
    return _atual


def registrar(tokens_entrada: int, tokens_saida: int, segundos: float) -> None:
    _atual.chamadas += 1
    _atual.tokens_entrada += tokens_entrada
    _atual.tokens_saida += tokens_saida
    _atual.segundos_no_modelo += segundos


def atual() -> Medicao:
    return _atual
