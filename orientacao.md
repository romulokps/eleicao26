# Orientações do projeto (registro vivo)

> Atualizado periodicamente. Fonte: pedido do usuário em 2026-10-26.

## Objetivo
2º turno de **25/10/2026**, cargo **Presidente**, Brasil inteiro (UF e cargo parametrizáveis).
Votação deveria terminar às 17h (Brasília); houve prorrogação até 19h em alguns locais.

1. **% de urnas fechadas** até 17:30, 18:00, 18:30, 19:00 e depois de 19:00 —
   acumulado e por faixa; contando seções e ponderado por comparecimento; por UF e Brasil.
2. **Resultado oficial** (todas as urnas) + 4 simulações excluindo seções que fecharam
   DEPOIS de 17:30, 18:00, 18:30 e 19:00. Para cada uma: votos e % válidos de cada
   candidato, margem, nº de seções e eleitores excluídos, e se o vencedor muda.

## Restrições de armazenamento/processamento (prioridade)
- Tudo roda no **GitHub Actions**. Matrix por UF (27 + ZZ), max-parallel razoável,
  `workflow_dispatch` com inputs (cargo, ufs).
- **Nunca** salvar brutos (.bu, .imgbu, .logjez, .rdv) em disco/repo: baixar em memória,
  extrair, descartar. Não baixar .logjez nem .rdv.
- Baixar só o mínimo: priorizar .bu (ASN.1) decodificado com a spec da "Documentação técnica
  do software da urna eletrônica" do TSE (2026, ou 2022 como base). Alternativa: .imgbu (texto).
  Testar os dois em 20 seções e escolher o menor/mais confiável.
- Não usar CSV bweb dos Dados Abertos.
- Saída por UF: parquet zstd, 1 linha/seção, colunas: uf, mun, zona, secao,
  hora_fechamento (min desde 00:00, int16), aptos, comparecimento, votos_cand1, votos_cand2,
  brancos, nulos, flag_problema (tipos enxutos int32/categorical). Upload como artifact;
  job final faz merge e gera relatório.
- No repo: só código, `dados/secoes_<cargo>.parquet`, `relatorio.md`, 1–2 PNGs. `.gitignore`
  para o resto. Sem Git LFS.
- Download assíncrono (httpx), concorrência ~15/job, retry com backoff, timeout, checkpoint
  (retoma sem rebaixar seções processadas).

## Fonte dos dados
- `https://resultados.tse.jus.br/oficial/comum/config/ele-c.json` → código da eleição do 2º turno.
- Seções: `.../oficial/ele2026/arquivo-urna/<eleicao>/config/<uf>/<uf>-p<eleicao>-cs.json`
- Por seção: `.../dados/<uf>/<mun>/<zona>/<secao>/...-aux.json` → nomes dos arquivos (e hashes).
  Confirmar a estrutura real de 2026 antes de escalar.
- **Não** usar dt/ht/dg/hg dos JSON de resultados (são de totalização/geração).
- Fuso: verificar se o horário no BU é Brasília ou local (AC, AM, RO, RR, MT, MS…).
  Normalizar para Brasília e documentar.
- Seções sem BU, urna substituída, votação manual, dados faltando: `flag_problema`,
  contar no relatório, nunca descartar em silêncio.

## Validação
- Rodar antes uma UF pequena (RR ou AP) e conferir soma de votos com o oficial da UF.
- No relatório, cenário "todas as urnas" deve bater com o total oficial; se não, mostrar diferença.

## Relatório (relatorio.md)
- Distribuição de fechamento (Brasil + UF), histograma em faixas de 15 min de 17:00 a 19:30+.
- Tabela oficial vs. cortes 17:30 / 18:00 / 18:30 / 19:00.
- UFs/municípios que concentram seções tardias.
- Limitações: fechamento após 17h pode ser fila legítima; fuso; seções com problema.

## Diário de decisões / descobertas
- 2026-10-26: o container da sessão Claude não alcança `resultados.tse.jus.br` (bloqueio da
  política de rede); toda a exploração é feita dentro do GitHub Actions.
- 2026-10-26: a integração não tem permissão para `workflow_dispatch` via API; a sonda (removida depois de usada)
  (`probe.yml`) também dispara por push em `claude/**` lendo `probe_args.txt`.
  O workflow principal mantém `workflow_dispatch` para uso manual pelo usuário.
- 2026-10-26: **ele-c.json** → pleito `3221` (ele2026, 25/10/2026); eleição `6258` = "Eleição Ordinária Federal -
  2026 2º Turno" (Presidente, cargo 1). Governador 2º turno = eleição `6260` (cargo 3). Descoberta automática em
  `src/tse.py::descobrir_eleicao`.
- 2026-10-26: **cs.json** (`arquivo-urna/3221/config/<uf>/<uf>-p003221-cs.json`): `abr[].mu[].zon[].sec[]` com
  `ns`; entradas com `nsp` são **seções agregadas** (sem BU próprio; votos no BU da principal) e `nsa` lista as
  agregadas da principal. `da/ha` = horário de recebimento (NÃO usar).
- 2026-10-26: **aux.json** (`dados/<uf>/<mun>/<zona>/<secao>/p003221-<uf>-m<mun>-z<zona>-s<secao>-aux.json`):
  `hashes[].{hash, st, arq[{nm, tp}]}`; arquivos em `<dir>/<hash>/<nm>`, ex. `o03221rr0312300070001-bu.dat`.
  Tipos: bu, imgbu, log, rdv, vota.
- 2026-10-26: **.imgbu dá 404 em 20/20 seções** (não publicado em 2026) → decisão: usar **.bu** (≈800–960 B).
- 2026-10-26: Spec ASN.1 oficial: site do TSE devolve 403 ao runner e não resolve neste container → decodificador
  DER próprio (`src/bu.py`) seguindo a estrutura do `bu.asn1` de 2022, conferido campo a campo em BUs reais e
  validado em 20/20 seções (comparecimento = soma dos votos). Hash do aux não é SHA simples do BU (não validado).
- 2026-10-26: **Fuso**: BU grava hora LOCAL (RR abre 07:00 → UTC−4). Sem horário de verão. Normalização: por
  município, moda de (8h − hora local de abertura); padrão por UF como fallback. Exterior: relativo às 8h locais.
- 2026-10-26: Resultado oficial: `ele2026/6258/dados/<uf>/<uf>-c0001-e006258-u.json` (e `br`). Usado só para
  validação (votos), nunca para horário.
- 2026-10-26: Disparo: `execucao.json` (push) ou `workflow_dispatch` em `coleta.yml`. Primeiro: RR (validação).
- 2026-10-26: **Validação RR OK**: soma dos 1.519 BUs = oficial exatamente (Lula 83.505; Flávio Bolsonaro 219.675;
  brancos 2.176; nulos 3.241; comparecimento 308.597; aptos 401.540). 108 seções agregadas; 8 urnas de contingência
  (flag 16); fuso +1h inferido nos 15 municípios. Velocidade ≈76 seções/s com concorrência 15, ≈1,5 KB/seção.
- 2026-10-26: Rodada Brasil (27 UFs + ZZ) disparada com commit do parquet/relatório ao final.
- 2026-10-26: Rodada Brasil 1 (run 40260109247): 27 UFs ok em ~1h (SP 103.656 seções a 43 seç/s, bate exato);
  MG levou 2h10. Soma Brasil ficou −1,44 mi de comparecimento vs oficial: 5.619 seções sem aux/BU por **falha
  transitória** (S3 do TSE devolve 403 sob carga e o cliente tratava 403 como inexistente). Correção: 403/404
  re-tentados 3×, repescagem de falhas ao fim da coleta, watchdog de 300 s por seção. Re-execução retoma do
  checkpoint (cache `ckpt-<cargo>-<uf>-`), re-baixando só as falhas.
- 2026-10-26: Rodada 2 (retomada): Brasil bate com o oficial exceto ZZ (−445/−353/−12/−21/−831). Causa: 70
  seções do exterior **sem `-bu.dat`**: apuradas pelo Sistema de Apuração (`-busa.dat`, mesmo formato ASN.1;
  sem horário de urna) ou **"Nao instalada"** (hash "0"). Coleta passa a usar busa (flag 32) e a marcar não
  instaladas (flag 2048, sem nova tentativa).
- 2026-10-26: Fuso inferido: AM tem 11 municípios em UTC−5 (+2h, ex. Tabatinga, Itamarati); Fernando de
  Noronha −1h; demais = padrão da UF.
