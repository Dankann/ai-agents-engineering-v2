# Nota de avaliação · Encontro 5

**Equipe:**
**Integrantes:**
**Domínio:** caso Aurora

> Uma página. As tabelas das seções 1, 2 e 4 saem prontas do Passo 6 do notebook 02. O que vale nota é o
> raciocínio das seções 3, 4 e 5: números que aguentam o teste do ruído e uma decisão defendida.

## 1 · Golden set do grupo

8 perguntas do banco de produção, com o gabarito que o grupo escreveu a partir da wiki. O arquivo
`encontro-05/golden-equipe.json` está no fork.

| id | pergunta | desfecho | fontes | contém | não contém |
|---|---|---|---|---|---|
| B16 | Qual o valor do auxílio-creche? | responder | beneficios-auxilio-creche | 600 | |
| B04 | Qual a diária máxima de hotel numa viagem para uma capital? | responder | fin-viagens-e-reembolso | 450 | R$ 320 |
| B07 | Em quanto tempo preciso compensar as horas do banco de horas? | responder | rh-jornada-e-banco-de-horas | 6 meses / seis meses | |
| B05 | Levei um cliente para jantar e pedimos vinho. A bebida é reembolsada? | responder | fin-viagens-e-reembolso | não é reembolsad / não são reembolsad / não reembols / não pode ser reembolsad | |
| B13 | Meu filho nasceu há 40 dias. Ainda dá para incluir ele no plano de saúde sem carência? | responder | beneficios-plano-de-saude | novembro | |
| B17 | Posso trabalhar duas semanas de Portugal? | responder | rh-trabalho-remoto | 30 dias | |
| B18 | Qual o horário do refeitório do escritório? | nao_sei | | | |
| B22 | Sou contratado como PJ. Tenho direito ao vale-refeição? | escalar | | | |

De onde saiu cada gabarito: B16 em `beneficios-auxilio-creche` §1.1 (R$ 600); B04 em `fin-viagens-e-reembolso` §6.1
(R$ 450 em capitais, R$ 320 nas demais, por isso o 320 é o valor proibido); B07 em `rh-jornada-e-banco-de-horas`
§3.2; B05 em `fin-viagens-e-reembolso` §5.2 (bebida alcoólica não é reembolsada nem com cliente); B13 em
`beneficios-plano-de-saude` §5.2 e §5.3; B17 em `rh-trabalho-remoto` §2.2. Para B18 e B22 a busca textual na wiki não
achou refeitório, PJ nem bônus: B18 é "não sei" porque a wiki é omissa, e B22 vai ao RH porque é uma pergunta sobre o
direito de quem pergunta, com um tipo de contrato que a wiki não cobre.

**Um gabarito difícil de decidir:** B13. Uma leitura é "escalar", porque a pessoa pergunta se o filho *dela* pode
entrar no plano. A outra é "responder", porque a wiki diz com todas as letras que passados 30 dias a inclusão só
acontece na janela de novembro e com carência. Ficamos com "responder": a regra é objetiva e não depende da análise
do RH, ao contrário do auxílio-creche, cuja página manda a elegibilidade para o RH. A produção ficou dividida (4 das
5 amostras da v1 escalaram e o juiz reprovou 2 delas), o que mostra que o caso é mesmo ambíguo para o agente.

## 2 · Placar

Golden set da turma (25 casos) mais o do grupo (8), 5 amostras de cada.

| versão | acerto (IC 90%) | pass^5 | instáveis | US$/acerto | p95 (s) | loops |
|---|---|---|---|---|---|---|
| v1 · produção | 72% (61%–83%) | 58% | 11/33 | 0.00079 | 9.7 | 12% |
| v2 · prompt enxuto (PR #42) | 75% (62%–86%) | 67% | 5/33 | 0.00047 | 5.7 | 2% |
| v3 · modelo mais barato | 98% (94%–100%) | 94% | 2/33 | 0.00022 | 4.4 | 0% |

Leitura: os intervalos da v1 e da v2 se sobrepõem quase por inteiro, então não há como separar as duas só pelo
acerto. A v3 fica acima de ambas, com o intervalo inteiro acima de 90%, e também é a mais barata e a mais rápida.
Dois casos do grupo, B18 e B17, nunca acertam na v1; a v3 acerta os dois nas 5 amostras.

## 3 · Regressão ou ruído

- **Ruído (teste A/A da v1):** o acerto variou até 9 pontos entre duas rodadas da mesma versão (4 em média).
- **PR #42:** diferença de +2% (IC 90%: -6% a +11%). Veredito: não dá para afirmar. Casos que mudaram: pioraram P1, R1 e G5; melhoraram C2, B13 e B22.
- **Modelo barato:** diferença de +25% (IC 90%: +14% a +37%). Veredito: melhora. Casos que mudaram: piorou N1; melhoraram S1, S2, P1, R1, R2, G5, G6, B13, B17, B18 e B22.

**Os casos do grupo mudaram alguma conclusão?** Com só os 8 casos do grupo, a v2 contra a v1 dá +20% (IC 90%: +0% a
+45%), ainda "não dá para afirmar", mas o intervalo é largo demais para valer algo com 8 casos. O que mudou foi a
leitura da v2: os casos do grupo (B13 e B22) mostram que o prompt enxuto reduz a instabilidade onde a v1 oscilava
entre responder e escalar, algo que o golden da turma sozinho não mostrava. A média da v2 fica em +2%, abaixo do
ruído de 9 pontos, e esconde regressões reais (P1, G5 e R1 caem a 0%). A v3 passa do ruído por uma margem grande.

## 4 · SLOs e gate

| SLO | por que esse número (e quem na Aurora concordaria) |
|---|---|
| acerto ≥ 85% | O ruído é de até 9 pontos, e v1 e v2 ficam 10 a 13 pontos abaixo. Quem responde por RH e jurídico aceitaria 1 resposta errada em cada 7 em benefícios? O alvo de 85% deixa uma folga acima do ruído. |
| aprovado_pelo_juiz ≥ 90% | É o único SLI de qualidade que dá para medir em produção, onde não há gabarito. A v1 faz 93% e a v2 87%, então o piso de 90% barra a v2 sem punir o que roda hoje. O RH validaria a rubrica do juiz. |
| custo_por_acerto ≤ US$ 0.0005 | Cerca de 60% do custo atual da v1 (0.00079). Quem paga a conta (Financeiro) concordaria, porque o custo por resposta certa já cai com a v2 e a v3. |
| p95_segundos ≤ 8.0 | O colaborador com pior experiência espera até 9.7 s na v1. O alvo de 8 s exige melhora sobre a produção de hoje sem pedir o desempenho da v3, e a TI e o RH concordariam com ele. |
| bateu_limite ≤ 2% | Cada loop custa caro e termina sem resposta. A v1 faz 12%. A TI aceitaria até 1 em 50. |

| SLO | v1 | v2 | v3 |
|---|---|---|---|
| acerto ≥ 85% | **FALHA** (72%) | **FALHA** (75%) | passa (98%) |
| aprovado_pelo_juiz ≥ 90% | passa (93%) | **FALHA** (87%) | passa (96%) |
| custo_por_acerto ≤ US$ 0.00050 | **FALHA** (US$ 0.00079) | passa (US$ 0.00047) | passa (US$ 0.00022) |
| p95_segundos ≤ 8.0s | **FALHA** (9.7s) | passa (5.7s) | passa (4.4s) |
| bateu_limite ≤ 2% | **FALHA** (12%) | passa (2%) | passa (0%) |

**A decisão:** a v3 (modelo mais barato) vai para produção, no lugar da v1. É a única que passa nos 5 SLOs, e a
melhora de +25% (IC 90%: +14% a +37%) é maior que o ruído de 9 pontos. A v2 não: não passa em acerto nem no juiz, e a
diferença contra a v1 não se distingue do ruído. Ressalva: a v3 regride em N1 (licença-paternidade, de 100% para 40%),
um caso de valor que ela manda ao RH 3 vezes em 5. É um erro para o lado seguro, mas é uma resposta que a wiki dá
sozinha. Subimos a v3 com N1 monitorado, e o plano é ajustar o prompt para não tratar "quantos dias eu tenho" como
pergunta de elegibilidade. Mudaríamos de ideia se, ao refazer o placar com mais amostras de produção, o acerto da v3
caísse abaixo de 85% ou se o RH achasse que o excesso de encaminhamentos pesa mais que o ganho.

## 5 · Um atendimento por dentro

**Caso, versão e amostra:** N1 ("Quantos dias de licença-paternidade eu tenho?"), v3, amostra 0 (errou).
**O que a cascata mostra** (passos, onde foi o tempo, o que a busca devolveu): 2 passos do modelo e 1 busca, 3.72 s e
US$ 0.00021 no total, 1748 tokens. O passo 1 (1.86 s) pediu `buscar_politicas`. A busca levou 0.2 ms e devolveu três
trechos de `rh-licencas`, a página certa. O passo 2 (1.86 s, 1067 tokens) pediu `escalar_para_rh`, em vez de
responder com os 20 dias que a página traz.
**Diagnóstico** (camada da pirâmide em que o problema aparece primeiro, e o que consertaria): o problema aparece no
passo do agente, depois de a busca acertar. O modelo entendeu "quantos dias eu tenho" como pergunta de elegibilidade
individual ("análise individual de elegibilidade deve ser feita pelo RH", diz a justificativa) e escalou. As amostras
1 e 3 repetem o erro, e as 2 e 4 respondem 20 dias. Consertaria o prompt, separando a pergunta de regra geral ("quantos
dias a política dá") do pedido de confirmar o direito de uma pessoa, e acrescentando N1 e casos parecidos ao golden.

---

*Opcional, para equipes que trocaram de domínio:* três perguntas da produção da empresa de vocês que
entrariam no golden set, e o SLO de qualidade que o negócio aceitaria.
