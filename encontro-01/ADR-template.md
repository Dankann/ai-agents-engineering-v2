# Agent Decision Record — [nome da equipe]

**Caso:** [Dúvidas Internas do Colaborador, ou o domínio da equipe, se aprovado]
**Data:** [data] · **Integrantes:** [nomes]
**Status:** proposta

## 1. Contexto

[Qual é o problema, para quem, e com quais restrições. 3 a 5 linhas.]

**Ação irreversível do caso:** [a ação que, depois de executada, não pode ser desfeita. Ex.: confirmar a um colaborador que ele é elegível a um benefício.]

## 2. Alternativas consideradas

Números do Hands-on 1 (mesmos 10 casos):

| Arquitetura | Acertos | Custo total | p50 | p95 | Custo por acerto | Variou entre execuções? |
|---|---|---|---|---|---|---|
| A · Prompt único | __/10 | US$ __ | __ s | __ s | US$ __ | — |
| B · Workflow | __/10 | US$ __ | __ s | __ s | US$ __ | — |
| C · Agente em loop | __/10 | US$ __ | __ s | __ s | US$ __ | __ de 10 casos |

**Onde cada uma errou, e por quê:** [2 a 4 linhas. Ex.: "B errou c07 porque o documento conflitante está em outro tema."]

## 3. Decisão

[A arquitetura escolhida, em uma frase.]

**Escopo de autonomia:** [o que o sistema pode decidir sozinho, e o que não pode.]

**Critério de parada** (se houver agente): [ex.: no máximo 6 passos por pergunta.]

## 4. Trade-offs assumidos

[O que a equipe aceita perder com essa escolha: custo, tempo, capacidade de explicar a resposta, risco.]

## 5. Critério de reversão

[A condição mensurável que faria a equipe voltar atrás. Deve dizer o que medir, o limite e para onde voltar.]

Exemplo de critério forte: *"Voltar para workflow se, nos casos de teste, o agente não superar o workflow em [__] acertos, ou se o custo por acerto passar de [US$ __]."*
