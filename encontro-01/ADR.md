# Agent Decision Record — [nome da equipe]

**Caso:** Dúvidas Internas do Colaborador (Aurora Tecnologia)
**Data:** [data] · **Integrantes:** [nomes]
**Status:** proposta

## 1. Contexto

A Aurora quer um assistente que responda dúvidas de colaboradores com base em 12 documentos de política: 5 de RH, 4 de TI e 3 de Benefícios. Toda resposta precisa citar as fontes e seguir o contrato JSON (`responder`, `escalar` ou `nao_sei`). Quando a informação não existe ou os documentos se contradizem, o assistente diz que não sabe. Quando a pessoa pergunta se ela mesma tem direito a um benefício, o caso vai para o RH.

**Ação irreversível do caso:** confirmar a um colaborador que ele é elegível a um benefício. Por isso toda pergunta de elegibilidade é escalada para o RH, em qualquer arquitetura.

## 2. Alternativas consideradas

Números do Hands-on 1, mesmos 10 casos, Claude Haiku 4.5. São duas rodadas completas das três arquiteturas, feitas em 2026-10-01. Onde as rodadas diferem, a célula mostra as duas.

| Arquitetura | Acertos | Custo total | p50 | p95 | Custo por acerto | Variou entre execuções? |
|---|---|---|---|---|---|---|
| A · Prompt único | 10/10 e 9/10 | US$ 0,0403 | 2,0 s | 3,0 a 3,4 s | US$ 0,0040 a 0,0045 | 1 de 10 casos (c07) |
| B · Workflow | 7/10 e 7/10 | US$ 0,016 a 0,017 | 1,9 a 2,2 s | 2,4 a 2,6 s | US$ 0,0023 a 0,0025 | nenhum |
| C · Agente em loop | 9/10 e 10/10 | US$ 0,065 a 0,071 | 4,6 s | 6,4 a 6,5 s | US$ 0,0065 a 0,0079 | 1 de 10 casos (c07) |

Por pergunta, A gasta cerca de 3.300 tokens de entrada numa única chamada. B gasta cerca de 1.100 em duas chamadas, e C entre 4.200 e 4.700 em duas chamadas, em média.

**Onde cada uma errou, e por quê:** B errou os mesmos três casos nas duas rodadas. No c05 (ambíguo) e no c10 (multi-passo) escalou para o RH: o classificador escolhe um único tema, e a resposta estava em outro tema ou em dois. No c07 (conflito) respondeu quando devia dizer `nao_sei`, porque só viu os documentos de um tema e não encontrou a contradição. A errou o c07 numa das rodadas: tinha os dois documentos em mãos e mesmo assim respondeu, em vez de apontar a contradição. C errou o c07 numa rodada com uma saída fora do contrato. O c07 é o caso instável: nenhuma arquitetura acertou nas duas rodadas.

Uma ressalva sobre a origem dos números: as rodadas de B e C usaram a solução de referência dos TODOs. A implementação da própria equipe está no repositório, mas não foi medida, porque a conta da API ficou sem crédito. A só tem a versão pronta, então seus números não dependem disso.

## 3. Decisão

Para o corpus de hoje, a Aurora deve usar a arquitetura A, prompt único.

Com 12 documentos, A acerta tanto quanto o agente (9 ou 10 de 10), custa de 30% a 50% menos por acerto e responde em menos da metade do tempo. O agente não ganhou nenhum caso que A tenha perdido. O workflow é o mais barato, mas erra 3 de 10, e um desses erros (c07) é uma resposta afirmativa onde devia haver um "não sei".

**Escopo de autonomia:** nenhum. O modelo recebe todos os documentos e a pergunta numa única chamada, sem ferramentas. Não decide quando buscar nem quantas vezes. A regra de escalar elegibilidade para o RH está na política de resposta e vale sempre.

**Critério de parada:** não se aplica a A. Se a equipe voltar para C, o limite é de 6 passos por pergunta. O c10, o caso mais difícil, precisa de cerca de 3 passos (duas buscas e a resposta), e 6 deixa folga para uma busca extra sem deixar um agente perdido gastar sem limite.

## 4. Trade-offs assumidos

- O custo cresce com o corpus, porque cada pergunta leva todos os documentos. Com 12 isso dá cerca de 3.300 tokens. Com milhares de documentos, a arquitetura deixa de caber no contexto e de valer o custo.
- A não deixa rastro de busca, ao contrário do agente. Para auditar uma resposta errada, restam só as fontes citadas.
- O conflito do c07 continua instável: A acertou uma das duas vezes. A equipe aceita esse risco hoje porque o agente também não foi melhor nesse caso.

## 5. Critério de reversão

Voltar para o agente em loop (C, com limite de 6 passos) se qualquer uma destas condições acontecer:

- o corpus passar de 50 documentos, ou a entrada de A passar de 15.000 tokens por pergunta;
- nos 10 casos de teste, rodados 3 vezes, C acertar pelo menos 1 caso a mais que A em média;
- o custo por acerto de A passar de US$ 0,0065, o melhor valor medido para C.
