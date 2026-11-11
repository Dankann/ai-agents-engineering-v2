# Tool Contract Sheet · Equipe [nome da equipe]

**Encontro 2 · Entrega de 10%: esta planilha e o código** · Caso: [Aurora Tecnologia ou domínio próprio]

Uma linha por ferramenta do caso: as seis do hands-on e as que o ADR da equipe exigir. Equipe que trocou de domínio preenche com as ferramentas do próprio caso.

**A entrega é documento e código.** Cada linha descreve uma ferramenta que existe no fork da equipe, com contrato implementado. Linha sem código correspondente vai marcada como *planejada*.

---

## 1. Catálogo

**Antes de cada linha, respondam a coluna "Quem decide":** essa chamada precisa ser escolhida pelo modelo, ou pode ser um passo fixo do workflow? Toda linha com "Modelo" precisa justificar, na seção 2, por que o código não poderia decidir.

| Nome | Quem decide | Descrição | Entrada | Saída | Escopo | Criticidade | Reversível |
|---|---|---|---|---|---|---|---|
| `abrir_chamado_ti` *(exemplo)* | Modelo | Cria chamado quando a base de TI não resolve ou o colaborador pede | categoria (enum), descricao (15–500), urgencia (enum) | id, status, prazo | Colaborador autenticado; só TI | Média | Com custo |
| `consultar_politica_rh` | Modelo | Busca nas políticas de RH, com tema opcional | pergunta (até 300), tema (enum de 6) | id, titulo, atualizado_em, trecho | Leitura da wiki de RH | Baixa | Sim |
| `buscar_base_ti` | Modelo | Busca na base de TI antes de responder ou abrir chamado | pergunta (até 300) | id, titulo, atualizado_em, trecho | Leitura da wiki de TI | Baixa | Sim |
| `abrir_chamado_ti` | Modelo | Abre chamado quando o colaborador pede ou a base não resolve; não repetir após timeout | categoria (enum), descricao (15 a 500), urgencia (enum) | id, status, categoria, urgencia, prazo_atendimento | Cria chamado no service desk; só TI | Média | Com custo |
| `consultar_regra_beneficio` | Modelo | Regra vigente de um benefício | beneficio (enum de 3), pergunta (até 300) | id, titulo, atualizado_em, trecho | Leitura da wiki de benefícios | Baixa | Sim |
| `verificar_elegibilidade_beneficio` | Modelo | Pré-análise de um colaborador; só o RH confirma | colaborador_id (até 20), beneficio (enum de 3) | colaborador_id, beneficio, pre_analise, criterios_verificados, aviso | Lê o cadastro de RH; CPF e salário ficam fora da saída | Alta | Sim |
| `consultar_rede_credenciada` | Modelo | Prestadores ativos da rede por cidade, tipo, especialidade e 24h | cidade (obrigatória), tipo (enum de 4), especialidade, apenas_24h (boolean) | id, prestador, tipo, especialidades, cidade, uf, bairro, telefone, atende_24h | Leitura da planilha da rede; no máximo 5 resultados; valor negociado e observação interna ficam fora | Média | Sim |

**Como preencher cada coluna:**

- **Nome:** verbo + objeto, na linguagem do domínio.
- **Quem decide:** `Modelo` (o agente escolhe) ou `Código` (passo fixo do workflow).
- **Descrição:** resumida aqui. A versão completa vai na seção 3, com o **quando não usar**.
- **Entrada:** parâmetros, tipos e restrições (enum, obrigatório, limites).
- **Saída:** só os campos que voltam ao modelo.
- **Escopo:** quem pode chamar, em nome de quem, que dados alcança.
- **Criticidade:** Baixa, Média ou Alta. O que acontece se ela falhar ou for chamada errado?
- **Reversível:** `Sim` (nada muda no mundo), `Com custo` (desfaz, mas alguém já viu) ou `Não`.

## 2. Justificativas

Para cada ferramenta com **Quem decide = Modelo**: por que essa chamada depende do conteúdo da pergunta e não pode ser um passo fixo?

- `consultar_politica_rh`: o tema da pergunta (férias, jornada, trabalho remoto) só aparece no texto do colaborador.
- `buscar_base_ti`: o assunto da dúvida define se a base de TI responde ou se é caso de chamado.
- `abrir_chamado_ti`: abrir ou não depende de o colaborador pedir e de a base resolver o problema, e a categoria e a urgência saem do relato.
- `consultar_regra_beneficio`: qual benefício e qual dúvida só se sabe lendo a pergunta.
- `verificar_elegibilidade_beneficio`: distinguir "qual é a regra" de "eu tenho direito" depende da frase do colaborador, e o id vem dele.
- `consultar_rede_credenciada`: cidade, tipo de prestador e necessidade de atendimento 24h vêm da pergunta.

## 3. Contratos completos

Colem aqui, ou referenciem no repositório, a descrição completa e o schema de cada ferramenta. Para as seis do hands-on, basta apontar `encontro-02/contratos.py` e `encontro-02/nova_ferramenta.py`.

As seis ferramentas estão implementadas: os contratos de `consultar_politica_rh`, `abrir_chamado_ti` e `verificar_elegibilidade_beneficio` em `encontro-02/contratos.py`, e implementação e contrato de `consultar_rede_credenciada` em `encontro-02/nova_ferramenta.py`.

## 4. Evidência do hands-on

**A quebra da dupla** (4, Saída verbosa):

| Versão | Acertos | Tool errada | Args inválidos | Chamados a mais | Dado sensível | Tokens/caso |
|---|---|---|---|---|---|---|
| Contrato da dupla | 11/17 | 0 | 0 | 0 | 0 | 7280 |
| Quebra 4 | 12/17 | 0 | 0 | 1 | 1 | 9385 |

Números de `python encontro-02/rodar.py --comparar 4`, com 17 casos e uma repetição. A quebra fez os tokens por caso subirem de 7280 para 9385, levou dado sensível ao contexto em um caso e abriu um chamado a mais no c13. O ponto a mais de acerto na quebra é variação de uma rodada só: o c06 falhou com o contrato da dupla e passou com a quebra. O CSV da rodada vai para `encontro-02/resultados/`, que o `.gitignore` ignora.

As rodadas usaram o provedor `claude_cli` (Claude Haiku 4.5 pela assinatura do Claude, chamadas de ferramenta emuladas, latência tirada do duration_api_ms e tokens descontada a base fixa do Claude Code).

O que dá para afirmar sem modelo, chamando a camada direto com os mesmos argumentos: com a quebra 4, `verificar_elegibilidade_beneficio` passa de 351 para 585 caracteres e passa a devolver CPF e salário (dado sensível no contexto). `consultar_rede_credenciada` não muda (995 caracteres nas duas versões, sem dado sensível), porque a implementação já descarta o valor negociado e a observação interna antes de devolver o registro.

**A ferramenta construída** (`consultar_rede_credenciada`): c16 passou e c17 passou na primeira versão (`python encontro-02/rodar.py --casos c16 c17 --detalhe`). Chamando a ferramenta direto, "CAMPINAS " devolve só os dois laboratórios ativos que fazem exame de sangue (sem o Taquaral, descredenciado), e Curitiba com `tipo` pronto_socorro e `apenas_24h` devolve só o Pinhão 24h (sem Barigui Sul nem Tingui). O código normaliza a cidade, descarta prestadores que não estão ativos, limita a 5 resultados e devolve o id da planilha como fonte.

**O que isso mudou no nosso contrato:** a descrição de `abrir_chamado_ti` ganhou a regra de não repetir a chamada depois de um timeout, já que o service desk cria o chamado mesmo quando estoura. As saídas de `verificar_elegibilidade_beneficio` e da rede ficaram só com os campos que o próximo passo usa.

## 5. A ação irreversível do ADR

A ação irreversível definida no ADR do Encontro 1 é: confirmar a elegibilidade de um colaborador a um benefício.

- Ela **não** é executada por nenhuma ferramenta do sistema: `verificar_elegibilidade_beneficio` só faz pré-análise (Reversível = `Sim`) e a confirmação fica com o RH.

> No Encontro 6, a coluna Reversível vira o eixo de impacto da matriz autonomia × impacto.
