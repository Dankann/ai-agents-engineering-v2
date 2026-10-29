# Encontro 5 · Evals, observabilidade e custo

**Pergunta do dia:** não existe `assert` em linguagem natural. Como um time ganha confiança para dar deploy?

## Antes da aula

**Nada a instalar.** Os notebooks deste encontro rodam no Google Colab, a partir do botão no topo de cada um. Basta uma conta Google.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/se-ai-agents-engineering/ai-agents-engineering-v2/blob/main/encontro-05/01-dentro-da-avaliacao.ipynb) `01-dentro-da-avaliacao.ipynb`, acompanhado ao vivo

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/se-ai-agents-engineering/ai-agents-engineering-v2/blob/main/encontro-05/02-hands-on-evals.ipynb) `02-hands-on-evals.ipynb`, o hands-on do grupo

Abra o notebook 01 antes da aula e rode só a primeira célula. Se aparecer "Tudo certo, pode seguir", você está pronto.

**Também não precisa de chave de API.** As respostas do modelo foram gravadas pelo professor, como no Encontro 4, com uma novidade: **cada caso foi gravado cinco vezes**, em três versões do agente. É essa variação que o encontro estuda.

> **Prefere rodar na sua máquina?** Funciona igual, a partir da raiz do repositório depois do Sync fork: `pip install -r requirements.txt` e `jupyter notebook encontro-05/`. Este encontro só precisa de `numpy`, `matplotlib` e `python-dotenv`.

## O que tem nesta pasta

| Arquivo | Para que serve |
|---|---|
| `01-dentro-da-avaliacao.ipynb` | Acompanhado ao vivo com o professor. Não tem entrega. |
| `02-hands-on-evals.ipynb` | O hands-on do grupo. Gera as tabelas da nota e o `golden-equipe.json`. |
| `NOTA-EVAL.md` | **O entregável.** Modelo de uma página para preencher. |
| `03-langfuse.ipynb` | O mesmo eval numa plataforma de mercado (Langfuse). O professor apresenta; quem quiser roda depois, com uma conta gratuita no Langfuse e sem chave de modelo. |
| `avaliacao.py` | A pirâmide de avaliação, o juiz, o intervalo de confiança, a comparação entre versões, os spans, o painel e os SLOs. |
| `golden-aurora.json` | O golden set da turma: os 19 casos dos Encontros 1 a 4 e mais 6 que vieram da produção (G1 a G6). |
| `banco-producao.json` | 24 perguntas da primeira semana em produção, **sem gabarito**. O grupo escreve o gabarito de 8 delas. |
| `dados/` | As gravações das respostas do modelo e dos juízes. Não mexa. |
| `preparo/` | Scripts do professor para gravar e conferir. A turma não usa. |

## As três versões do agente

O sistema avaliado é o **agente único da Aula 4**: a mesma busca, o mesmo contrato e a mesma camada.

| Versão | O que mudou |
|---|---|
| v1 · produção | nada: é o agente da Aula 4 |
| v2 · prompt enxuto (PR #42) | um colega encurtou o prompt de sistema para economizar tokens |
| v3 · modelo mais barato | o mesmo prompt da v1, num modelo que custa menos por token |

## O entregável

`encontro-05/NOTA-EVAL.md` e `encontro-05/golden-equipe.json` no fork da equipe: o golden set do grupo, o placar das três versões com intervalo de confiança, o veredito "regressão ou ruído" sobre as duas mudanças, os SLOs do grupo com a decisão de deploy e um atendimento aberto na cascata. Os detalhes estão no topo do notebook 02.

---

## Para o professor: preparar o encontro

Uma vez por turma, na sua máquina, a partir da raiz do repositório, com o ambiente do Encontro 3 instalado (o `sentence-transformers` calcula os vetores das consultas novas) e o `.env` do Encontro 4 (`PROVEDOR=openai_compat`, `BASE_URL`, `API_KEY`, **com `TEMPERATURA` vazio**):

```bash
# 1. conferir os três modelos e os preços em encontro-05/preparo/config.json

# 2. gravar: 735 atendimentos e os juízes; por volta de US$ 1 e de 30 a 60 minutos
python encontro-05/preparo/gravar_replay.py

# 3. conferir que tudo roda sem chave
python encontro-05/preparo/gravar_replay.py --conferir

# 4. os números e a história da aula, a partir da sua gravação
python encontro-05/preparo/conferir_aula.py
```

Depois, faça commit da pasta `encontro-05/dados/`. Sem ela, os notebooks não rodam no Colab. Se editar os notebooks 01 ou 02, rode o passo 2 de novo: ele só chama a API para o que ainda não estiver gravado.

O passo 4 importa: os notebooks escolhem os exemplos sozinhos (o caso mais instável, o atendimento mais lento), mas a história da aula depende do que o modelo fez de verdade. O PR #42 regrediu? O modelo barato se pagou? O script conta essa história com os seus números e avisa se algum momento da aula ficou sem exemplo.

O notebook 03 precisa de uma conta no Langfuse ([cloud.langfuse.com](https://cloud.langfuse.com), plano gratuito) e das duas chaves do projeto nos Segredos do Colab. Rode-o na véspera: a Parte 1 leva o tempo real de um atendimento, e os experimentos da Parte 3 ficam no projeto, prontos para mostrar.
