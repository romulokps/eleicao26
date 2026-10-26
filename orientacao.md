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
- 2026-10-26: a integração não tem permissão para `workflow_dispatch` via API; a sonda
  (`probe.yml`) também dispara por push em `claude/**` lendo `probe_args.txt`.
  O workflow principal mantém `workflow_dispatch` para uso manual pelo usuário.
