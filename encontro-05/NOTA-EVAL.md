# Nota de avaliação · Encontro 5

**Equipe:**
**Integrantes:**
**Domínio:** caso Aurora / domínio próprio: _____ (riscar o que não vale)

> Uma página. As tabelas das seções 1, 2 e 4 saem prontas do Passo 6 do notebook 02. O que vale nota é o
> raciocínio das seções 3, 4 e 5: números que aguentam o teste do ruído e uma decisão defendida.

## 1 · Golden set do grupo

8 perguntas do banco de produção, com o gabarito que o grupo escreveu a partir da wiki. O arquivo
`encontro-05/golden-equipe.json` está no fork.

| id | pergunta | desfecho | fontes | contém | não contém |
|---|---|---|---|---|---|
| | | | | | |

**Um gabarito difícil de decidir** (id, as duas leituras possíveis e por que o grupo escolheu esta):

## 2 · Placar

Golden set da turma (25 casos) mais o do grupo (8), 5 amostras de cada.

> Pendente: estes números saíram de uma rodada com 26 casos (os 25 da turma e só o B16 do grupo). Refazer o
> placar depois que os 8 casos do grupo estiverem escritos.

| versão | acerto (IC 90%) | pass^5 | instáveis | US$/acerto | p95 (s) | loops |
|---|---|---|---|---|---|---|
| v1 · produção | 79% (68%–89%) | 65% | 8/26 | 0.00068 | 9.5 | 10% |
| v2 · prompt enxuto (PR #42) | 76% (62%–88%) | 73% | 2/26 | 0.00041 | 4.9 | 0% |
| v3 · modelo mais barato | 97% (92%–100%) | 92% | 2/26 | 0.00023 | 4.5 | 0% |

## 3 · Regressão ou ruído

Também calculado com 26 casos, a refazer com os 8 do grupo.

- **Ruído (teste A/A da v1):** o acerto variou até 4 pontos entre duas rodadas da mesma versão.
- **PR #42:** diferença de -3% (IC 90%: -10% a +4%). Veredito: não dá para afirmar. Casos que mudaram: pioraram P1, R1 e G5; melhorou C2.
- **Modelo barato:** diferença de +18% (IC 90%: +6% a +30%). Veredito: melhora. Casos que mudaram: piorou N1; melhoraram S1, S2, P1, R1, R2, G5 e G6.

**Os casos do grupo mudaram alguma conclusão?** (uma ou duas frases)

## 4 · SLOs e gate

| SLO | por que esse número (e quem na Aurora concordaria) |
|---|---|
| | |
| | |
| | |

| SLO | v1 | v2 | v3 |
|---|---|---|---|
| | | | |

**A decisão:** que versão vai para produção, contra o quê, com que números, e o que faria o grupo mudar de ideia.

## 5 · Um atendimento por dentro

**Caso, versão e amostra:**
**O que a cascata mostra** (passos, onde foi o tempo, o que a busca devolveu):
**Diagnóstico** (camada da pirâmide em que o problema aparece primeiro, e o que consertaria):

---

*Opcional, para equipes que trocaram de domínio:* três perguntas da produção da empresa de vocês que
entrariam no golden set, e o SLO de qualidade que o negócio aceitaria.
