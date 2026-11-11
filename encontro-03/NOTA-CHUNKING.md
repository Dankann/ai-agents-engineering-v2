# Nota de chunking · Equipe: ____________

Caso: (X) Aurora  ( ) domínio próprio: ____________

## 1. O que adotamos

Estratégia de chunking: por estrutura (um chunk por seção da página, com "Título > Seção" escrito no início do chunk).
Busca (vetor, BM25 ou híbrida): híbrida, vetor mais BM25.
Tratamento de versões e de autoridade: filtro `so_vigente` ligado (para cada política, só a página de vigência mais recente) e `so_oficial` ligado (descarta páginas que não são oficiais).
k (quantos trechos o agente recebe): 3.

## 2. Por quê

| configuração | normal | excecao | conflito | termo-exato | autoridade | total |
|---|---|---|---|---|---|---|
| base: tamanho 400 · vetor | 7/7 (0) | 2/2 (1) | 2/3 (3) | 3/3 (1) | 1/1 (0) | 15/16 (5) |
| estrutura · vetor | 6/7 (0) | 2/2 (0) | 2/3 (3) | 3/3 (0) | 1/1 (0) | 14/16 (3) |
| estrutura · híbrida | 6/7 (0) | 2/2 (0) | 1/3 (3) | 3/3 (0) | 1/1 (0) | 13/16 (3) |
| estrutura · híbrida · só vigente | 6/7 (0) | 2/2 (0) | 3/3 (0) | 3/3 (0) | 1/1 (0) | 15/16 (0) |
| estrutura · híbrida · vigente · oficial | 6/7 (0) | 2/2 (0) | 3/3 (0) | 3/3 (0) | 1/1 (0) | 15/16 (0) |

Formato: achou/casos (contaminados), com k=3, nos 16 casos que têm resposta.

Escolhemos a última linha. A mudança que mais pesou foi `só vigente`: os casos de conflito foram de 1/3 para 3/3 e os contaminados caíram de 3 para 0. O chunking por estrutura, sozinho, não aumentou o "achou" (14/16 contra 15/16 da base), mas reduziu os contaminados de 5 para 3, e a base de 400 caracteres contaminou 5 casos. A busca híbrida, sozinha, piorou o conflito (1/3) e o total (13/16), e só ficou boa depois do filtro de vigência. `só oficial` não mudou o placar nestes casos (a mesma linha, 15/16 e 0 contaminados). Mantivemos o filtro porque ele custa pouco e a wiki tem uma página com autoridade "resumo".

Fora do notebook, rodamos a configuração escolhida com outros valores de k: com k=1, 13/16 e 2 contaminados; com k=5, 16/16 e 0 contaminados. Ficamos em k=3 por ser o valor da tabela, mas com k=5 o caso N5 também é encontrado.

## 3. O que ela não resolve

O caso N5 ("Roubaram meu notebook do trabalho. O que eu faço?") continua falhando com k=3. O chunk certo existe e está inteiro (a seção "Defeito, quebra, perda ou roubo" de `ti-equipamentos`, que traz o boletim de ocorrência), mas a pergunta usa "roubaram" e o texto usa "roubo". Entram no top 3 o chunk de introdução de `ti-equipamentos`, uma seção de `rh-desligamento` sobre devolução de notebook e um erro de VPN; o chunk certo só aparece na quinta posição. A causa é de busca: o vocabulário da pergunta é diferente do da página e vários chunks falam de "notebook". Isso deveria ser tratado no retriever (k maior, ou um reranker sobre mais candidatos), e não no chunking.

As três perguntas sem resposta (S1, S2, S3) o placar não mede. A busca sempre devolve três trechos: para "A Aurora oferece previdência privada?", trouxe licenças, seguro de vida e plano odontológico. Nenhuma configuração de busca resolve isso. O "não sei" deve ser decidido pelo agente, na instrução e na leitura dos trechos, ou por um limiar de score, que não testamos.

## 4. O que a ingestão precisa garantir

| metadado | quem preenche | quando é atualizado | se estiver errado |
|---|---|---|---|
| `politica` | dono da página (campo `dono`) | ao criar a página; igual em todas as versões da mesma política | versões da mesma política não se agrupam e as duas respostas chegam ao agente |
| `vigencia` | dono da página | a cada nova versão da política | uma versão velha pode ser considerada a vigente e o agente responde com a regra antiga |
| `autoridade` | dono da página, revisado pela ingestão | ao criar a página e quando ela deixa de ser oficial | uma página de resumo passa por oficial, ou uma oficial é descartada e a resposta some |
| títulos e seções (cabeçalhos) | quem escreve a página | a cada edição | o chunking por estrutura corta no lugar errado e o prefixo "Título > Seção" perde o sentido |
