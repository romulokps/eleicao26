# Horário de encerramento das urnas e simulações de corte — Eleição Ordinária Federal - 2026 2º Turno — Presidente

Eleição 6258 (pleito 3221), 25/10/2026. UFs no relatório: 28 (AC, AL, AM, AP, BA, CE, DF, ES, GO, MA, MG, MS, MT, PA, PB, PE, PI, PR, RJ, RN, RO, RR, RS, SC, SE, SP, TO, ZZ).

Fonte: Boletins de Urna (arquivo `-bu.dat`, ASN.1/DER) publicados em resultados.tse.jus.br, campo `dataHoraEncerramento` do BU, normalizado para o horário de Brasília. Detalhes de método e limitações no fim do documento. Dados por seção em `dados/secoes_*.parquet`.

## Resumo

- Seções com BU processadas: **499.248**; com horário de encerramento: **493.629**; seções agregadas (votos no BU da seção principal): 17.931.
- Urnas encerradas (Brasil, % das seções): até 17:30 **98.46%**, até 18:00 **98.56%**, até 18:30 **98.63%**, até 19:00 **98.71%**; depois das 19:00: **1.29%** (6.350 seções).
- Vencedor com todas as urnas: **LULA (13)** (51.79% dos válidos, margem 4.381.714 votos). **O vencedor não muda** em nenhum dos 4 cortes.

## Validação: soma dos BUs × resultado oficial do TSE

Oficial TSE Brasil (totalização de 25/10/2026 23:26:38; seções totalizadas 499248 de 499248):

| Brasil | LULA | FLAVIO BOLSONARO | brancos | nulos | comparecimento |
|---|---:|---:|---:|---:|---:|
| soma dos BUs | 63.534.706 | 59.152.992 | 1.413.931 | 2.690.980 | 126.792.609 |
| oficial TSE | 64.256.232 | 59.826.041 | 1.430.496 | 2.723.305 | 128.236.074 |
| diferença | -721526 | -673049 | -16565 | -32325 | -1443465 |

**Não bate exatamente** — ver diferença acima e seções com problema abaixo.

<details><summary>Por UF</summary>

| UF | LULA | FLAVIO BOLSONARO | brancos | nulos | comparec. | diferença BU−oficial (LULA, FLAVIO BOLSONARO, br, nu, comp) |
|---|---:|---:|---:|---:|---:|---:|
| AC | 144.513 | 287.715 | 5.016 | 16.410 | 453.654 | +0, +0, +0, +0, +0 |
| AL | 1.152.621 | 744.140 | 16.983 | 37.888 | 1.951.632 | +0, +0, +0, +0, +0 |
| AM | 1.112.636 | 934.795 | 17.429 | 51.054 | 2.115.914 | -33147, -40450, -895, -1653, -76145 |
| AP | 222.968 | 198.674 | 3.320 | 5.013 | 429.975 | +0, +0, +0, +0, +0 |
| BA | 6.375.365 | 2.571.845 | 91.092 | 230.542 | 9.268.844 | -109893, -36916, -1629, -4765, -153203 |
| CE | 4.036.124 | 1.819.478 | 56.386 | 112.855 | 6.024.843 | +0, +0, +0, +0, +0 |
| DF | 823.620 | 977.554 | 22.325 | 41.049 | 1.864.548 | -1604, -1988, -61, -79, -3732 |
| ES | 1.001.965 | 1.294.504 | 33.080 | 79.665 | 2.409.214 | +0, +0, +0, +0, +0 |
| GO | 1.560.971 | 2.308.156 | 42.533 | 71.994 | 3.983.654 | -24584, -37178, -681, -1183, -63626 |
| MA | 2.735.594 | 1.182.571 | 29.817 | 56.698 | 4.004.680 | -72637, -47400, -1038, -2016, -123091 |
| MG | 6.008.755 | 5.855.414 | 154.401 | 270.528 | 12.289.098 | -342344, -386372, -9740, -16649, -755105 |
| MS | 606.301 | 896.917 | 14.383 | 21.839 | 1.539.440 | -22672, -30975, -575, -798, -55020 |
| MT | 694.167 | 1.351.099 | 15.431 | 24.637 | 2.085.334 | +0, +0, +0, +0, +0 |
| PA | 2.690.449 | 2.199.940 | 36.501 | 62.683 | 4.989.573 | +0, +0, +0, +0, +0 |
| PB | 1.785.356 | 862.103 | 25.854 | 58.115 | 2.731.428 | -8703, -3107, -89, -233, -12132 |
| PE | 4.117.513 | 1.832.554 | 56.758 | 119.642 | 6.126.467 | +0, +0, +0, +0, +0 |
| PI | 1.653.989 | 525.859 | 16.137 | 43.845 | 2.239.830 | +0, +0, +0, +0, +0 |
| PR | 2.566.504 | 4.291.444 | 82.572 | 118.819 | 7.059.339 | +0, +0, +0, +0, +0 |
| RJ | 4.565.393 | 5.169.033 | 111.682 | 231.341 | 10.077.449 | +0, +0, +0, +0, +0 |
| RN | 1.324.508 | 698.822 | 18.642 | 57.809 | 2.099.781 | -89088, -38587, -1297, -4070, -133042 |
| RO | 294.446 | 674.382 | 8.361 | 11.300 | 988.489 | +0, +0, +0, +0, +0 |
| RR | 83.505 | 219.675 | 2.176 | 3.241 | 308.597 | +0, +0, +0, +0, +0 |
| RS | 2.824.552 | 3.874.378 | 89.463 | 101.245 | 6.889.638 | +0, +0, +0, +0, +0 |
| SC | 1.401.905 | 3.170.348 | 48.126 | 74.386 | 4.694.765 | -16409, -49723, -548, -858, -67538 |
| SE | 989.041 | 433.354 | 13.135 | 31.129 | 1.466.659 | +0, +0, +0, +0, +0 |
| SP | 12.119.274 | 14.139.178 | 389.606 | 716.331 | 27.364.389 | +0, +0, +0, +0, +0 |
| TO | 442.962 | 467.916 | 8.059 | 35.826 | 954.763 | +0, +0, +0, +0, +0 |
| ZZ | 199.709 | 171.144 | 4.663 | 5.096 | 380.612 | -445, -353, -12, -21, -831 |

</details>

## 1. Percentual de urnas encerradas por horário (Brasília)

Faixas: “até 17:30” = encerramento antes de 17:30:00; “17:30–18:00” = de 17:30:00 a 17:59:59; etc. Só seções com horário de encerramento no BU.

| Brasil | seções | % seções | % seções acum. | comparecimento | % comparec. | % comparec. acum. |
|---|---:|---:|---:|---:|---:|---:|
| até 17:30 | 486.014 | 98.46 | 98.46 | 124.581.754 | 98.26 | 98.26 |
| 17:30–18:00 | 528 | 0.11 | 98.56 | 140.245 | 0.11 | 98.37 |
| 18:00–18:30 | 316 | 0.06 | 98.63 | 84.298 | 0.07 | 98.43 |
| 18:30–19:00 | 421 | 0.09 | 98.71 | 125.748 | 0.10 | 98.53 |
| depois de 19:00 | 6.350 | 1.29 | 100.00 | 1.860.564 | 1.47 | 100.00 |

### Por UF — % das seções em cada faixa (ordenado pela % que fechou depois de 17:30)

| UF | seções | até 17:30 | 17:30–18:00 | 18:00–18:30 | 18:30–19:00 | depois de 19:00 |
|---|---:|---:|---:|---:|---:|---:|
| RJ | 37.675 | 91.19 | 0.34 | 0.50 | 0.53 | 7.45 |
| PE | 21.418 | 96.65 | 0.08 | 0.01 | 0.19 | 3.07 |
| BA | 34.952 | 97.00 | 0.16 | 0.02 | 0.14 | 2.67 |
| PB | 10.662 | 97.04 | 0.04 | 0.01 | 0.34 | 2.58 |
| SP | 103.656 | 98.10 | 0.20 | 0.10 | 0.08 | 1.52 |
| SE | 5.923 | 99.07 | 0.02 | 0.02 | 0.03 | 0.86 |
| ZZ | 1.281 | 99.45 | 0.31 | 0.23 | 0.00 | 0.00 |
| DF | 6.955 | 99.53 | 0.23 | 0.00 | 0.00 | 0.24 |
| MT | 8.287 | 99.84 | 0.05 | 0.00 | 0.00 | 0.11 |
| PI | 10.225 | 99.86 | 0.04 | 0.03 | 0.00 | 0.07 |
| AM | 7.907 | 99.89 | 0.10 | 0.01 | 0.00 | 0.00 |
| AL | 7.101 | 99.90 | 0.07 | 0.00 | 0.00 | 0.03 |
| MA | 17.586 | 99.90 | 0.07 | 0.01 | 0.00 | 0.02 |
| RN | 7.622 | 99.91 | 0.05 | 0.00 | 0.00 | 0.04 |
| PA | 20.827 | 99.91 | 0.05 | 0.00 | 0.00 | 0.04 |
| CE | 23.765 | 99.94 | 0.05 | 0.00 | 0.00 | 0.00 |
| AP | 1.914 | 99.95 | 0.05 | 0.00 | 0.00 | 0.00 |
| AC | 2.270 | 99.96 | 0.00 | 0.00 | 0.00 | 0.04 |
| RO | 4.698 | 99.96 | 0.02 | 0.02 | 0.00 | 0.00 |
| ES | 9.844 | 99.96 | 0.02 | 0.00 | 0.00 | 0.02 |
| MG | 49.086 | 99.97 | 0.03 | 0.00 | 0.00 | 0.00 |
| RS | 27.547 | 99.97 | 0.02 | 0.00 | 0.01 | 0.01 |
| GO | 15.441 | 99.97 | 0.02 | 0.01 | 0.00 | 0.01 |
| SC | 17.081 | 99.98 | 0.01 | 0.00 | 0.01 | 0.00 |
| MS | 6.861 | 99.99 | 0.01 | 0.00 | 0.00 | 0.00 |
| PR | 27.142 | 99.99 | 0.01 | 0.00 | 0.00 | 0.00 |
| RR | 1.519 | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| TO | 4.384 | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| BRASIL | 493.629 | 98.46 | 0.11 | 0.06 | 0.09 | 1.29 |

### Por UF — % acumulado das seções

| UF | até 17:30 | até 18:00 | até 18:30 | até 19:00 | todas (inclui >19:00) |
|---|---:|---:|---:|---:|---:|
| RJ | 91.19 | 91.53 | 92.02 | 92.55 | 100.00 |
| PE | 96.65 | 96.73 | 96.75 | 96.93 | 100.00 |
| BA | 97.00 | 97.16 | 97.18 | 97.33 | 100.00 |
| PB | 97.04 | 97.07 | 97.08 | 97.42 | 100.00 |
| SP | 98.10 | 98.30 | 98.40 | 98.48 | 100.00 |
| SE | 99.07 | 99.09 | 99.11 | 99.14 | 100.00 |
| ZZ | 99.45 | 99.77 | 100.00 | 100.00 | 100.00 |
| DF | 99.53 | 99.76 | 99.76 | 99.76 | 100.00 |
| MT | 99.84 | 99.89 | 99.89 | 99.89 | 100.00 |
| PI | 99.86 | 99.90 | 99.93 | 99.93 | 100.00 |
| AM | 99.89 | 99.99 | 100.00 | 100.00 | 100.00 |
| AL | 99.90 | 99.97 | 99.97 | 99.97 | 100.00 |
| MA | 99.90 | 99.98 | 99.98 | 99.98 | 100.00 |
| RN | 99.91 | 99.96 | 99.96 | 99.96 | 100.00 |
| PA | 99.91 | 99.96 | 99.96 | 99.96 | 100.00 |
| CE | 99.94 | 100.00 | 100.00 | 100.00 | 100.00 |
| AP | 99.95 | 100.00 | 100.00 | 100.00 | 100.00 |
| AC | 99.96 | 99.96 | 99.96 | 99.96 | 100.00 |
| RO | 99.96 | 99.98 | 100.00 | 100.00 | 100.00 |
| ES | 99.96 | 99.98 | 99.98 | 99.98 | 100.00 |
| MG | 99.97 | 99.99 | 99.99 | 100.00 | 100.00 |
| RS | 99.97 | 99.99 | 99.99 | 99.99 | 100.00 |
| GO | 99.97 | 99.99 | 99.99 | 99.99 | 100.00 |
| SC | 99.98 | 99.99 | 99.99 | 100.00 | 100.00 |
| MS | 99.99 | 100.00 | 100.00 | 100.00 | 100.00 |
| PR | 99.99 | 100.00 | 100.00 | 100.00 | 100.00 |
| RR | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| TO | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| BRASIL | 98.46 | 98.56 | 98.63 | 98.71 | 100.00 |

<details><summary>Por UF — ponderado por comparecimento (por faixa e acumulado)</summary>

| UF | até 17:30 | 17:30–18:00 | 18:00–18:30 | 18:30–19:00 | depois de 19:00 |
|---|---:|---:|---:|---:|---:|
| RJ | 90.28 | 0.32 | 0.48 | 0.62 | 8.31 |
| PE | 96.49 | 0.08 | 0.01 | 0.20 | 3.22 |
| BA | 96.51 | 0.17 | 0.03 | 0.16 | 3.12 |
| PB | 96.50 | 0.04 | 0.01 | 0.39 | 3.07 |
| SP | 98.04 | 0.22 | 0.10 | 0.09 | 1.55 |
| SE | 98.97 | 0.01 | 0.02 | 0.04 | 0.95 |
| ZZ | 99.50 | 0.20 | 0.29 | 0.00 | 0.00 |
| DF | 99.55 | 0.24 | 0.00 | 0.00 | 0.21 |
| MT | 99.81 | 0.05 | 0.00 | 0.00 | 0.13 |
| PI | 99.86 | 0.04 | 0.03 | 0.00 | 0.07 |
| AM | 99.89 | 0.09 | 0.01 | 0.00 | 0.00 |
| AL | 99.90 | 0.07 | 0.00 | 0.00 | 0.03 |
| MA | 99.92 | 0.06 | 0.01 | 0.00 | 0.02 |
| RN | 99.90 | 0.05 | 0.00 | 0.00 | 0.04 |
| PA | 99.91 | 0.04 | 0.00 | 0.01 | 0.05 |
| CE | 99.94 | 0.05 | 0.00 | 0.00 | 0.00 |
| AP | 99.94 | 0.06 | 0.00 | 0.00 | 0.00 |
| AC | 99.95 | 0.00 | 0.00 | 0.00 | 0.05 |
| RO | 99.96 | 0.02 | 0.02 | 0.00 | 0.00 |
| ES | 99.96 | 0.02 | 0.00 | 0.00 | 0.02 |
| MG | 99.97 | 0.02 | 0.00 | 0.00 | 0.00 |
| RS | 99.97 | 0.02 | 0.00 | 0.01 | 0.01 |
| GO | 99.96 | 0.02 | 0.01 | 0.00 | 0.01 |
| SC | 99.98 | 0.01 | 0.00 | 0.01 | 0.00 |
| MS | 99.98 | 0.02 | 0.00 | 0.00 | 0.00 |
| PR | 99.99 | 0.01 | 0.00 | 0.00 | 0.00 |
| RR | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| TO | 100.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| BRASIL | 98.26 | 0.11 | 0.07 | 0.10 | 1.47 |

| UF | até 17:30 | até 18:00 | até 18:30 | até 19:00 | todas (inclui >19:00) |
|---|---:|---:|---:|---:|---:|
| RJ | 90.28 | 90.59 | 91.07 | 91.69 | 100.00 |
| PE | 96.49 | 96.57 | 96.58 | 96.78 | 100.00 |
| BA | 96.51 | 96.69 | 96.72 | 96.88 | 100.00 |
| PB | 96.50 | 96.54 | 96.55 | 96.93 | 100.00 |
| SP | 98.04 | 98.26 | 98.36 | 98.45 | 100.00 |
| SE | 98.97 | 98.99 | 99.01 | 99.05 | 100.00 |
| ZZ | 99.50 | 99.71 | 100.00 | 100.00 | 100.00 |
| DF | 99.55 | 99.79 | 99.79 | 99.79 | 100.00 |
| MT | 99.81 | 99.87 | 99.87 | 99.87 | 100.00 |
| PI | 99.86 | 99.90 | 99.93 | 99.93 | 100.00 |
| AM | 99.89 | 99.99 | 100.00 | 100.00 | 100.00 |
| AL | 99.90 | 99.97 | 99.97 | 99.97 | 100.00 |
| MA | 99.92 | 99.98 | 99.98 | 99.98 | 100.00 |
| RN | 99.90 | 99.96 | 99.96 | 99.96 | 100.00 |
| PA | 99.91 | 99.95 | 99.95 | 99.95 | 100.00 |
| CE | 99.94 | 100.00 | 100.00 | 100.00 | 100.00 |
| AP | 99.94 | 100.00 | 100.00 | 100.00 | 100.00 |
| AC | 99.95 | 99.95 | 99.95 | 99.95 | 100.00 |
| RO | 99.96 | 99.98 | 100.00 | 100.00 | 100.00 |
| ES | 99.96 | 99.98 | 99.98 | 99.98 | 100.00 |
| MG | 99.97 | 99.99 | 100.00 | 100.00 | 100.00 |
| RS | 99.97 | 99.99 | 99.99 | 99.99 | 100.00 |
| GO | 99.96 | 99.98 | 99.99 | 99.99 | 100.00 |
| SC | 99.98 | 99.99 | 99.99 | 100.00 | 100.00 |
| MS | 99.98 | 100.00 | 100.00 | 100.00 | 100.00 |
| PR | 99.99 | 100.00 | 100.00 | 100.00 | 100.00 |
| RR | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| TO | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
| BRASIL | 98.26 | 98.37 | 98.43 | 98.53 | 100.00 |

</details>

## Histograma de encerramento (faixas de 15 min)

![Histograma](fig_histograma.png)

| faixa (Brasília) | seções | % seções | comparecimento | % comparec. |
|---|---:|---:|---:|---:|
| <17:00 | 0 | 0.00 | 0 | 0.00 |
| 17:00–17:15 | 484.483 | 98.15 | 124.172.489 | 97.93 |
| 17:15–17:30 | 1.531 | 0.31 | 409.265 | 0.32 |
| 17:30–17:45 | 258 | 0.05 | 68.405 | 0.05 |
| 17:45–18:00 | 270 | 0.05 | 71.840 | 0.06 |
| 18:00–18:15 | 199 | 0.04 | 53.782 | 0.04 |
| 18:15–18:30 | 117 | 0.02 | 30.516 | 0.02 |
| 18:30–18:45 | 22 | 0.00 | 5.760 | 0.00 |
| 18:45–19:00 | 399 | 0.08 | 119.988 | 0.09 |
| 19:00–19:15 | 6.314 | 1.28 | 1.851.889 | 1.46 |
| 19:15–19:30 | 18 | 0.00 | 4.625 | 0.00 |
| ≥19:30 | 18 | 0.00 | 4.050 | 0.00 |

<details><summary>Histograma por UF (nº de seções)</summary>

| UF | 17:00–17:15 | 17:15–17:30 | 17:30–17:45 | 17:45–18:00 | 18:00–18:15 | 18:15–18:30 | 18:30–18:45 | 18:45–19:00 | 19:00–19:15 | 19:15–19:30 | ≥19:30 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AC | 2267 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| AL | 7078 | 16 | 4 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |
| AM | 7855 | 43 | 6 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| AP | 1909 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| BA | 33717 | 188 | 36 | 19 | 4 | 4 | 2 | 48 | 931 | 2 | 1 |
| CE | 23715 | 36 | 8 | 5 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| DF | 6855 | 67 | 14 | 2 | 0 | 0 | 0 | 0 | 17 | 0 | 0 |
| ES | 9835 | 5 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| GO | 15422 | 14 | 2 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| MA | 17486 | 83 | 11 | 2 | 0 | 1 | 0 | 0 | 3 | 0 | 0 |
| MG | 49030 | 39 | 8 | 5 | 1 | 0 | 2 | 0 | 0 | 0 | 1 |
| MS | 6853 | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| MT | 8264 | 10 | 3 | 1 | 0 | 0 | 0 | 0 | 9 | 0 | 0 |
| PA | 20731 | 77 | 9 | 1 | 0 | 0 | 0 | 1 | 8 | 0 | 0 |
| PB | 10330 | 16 | 4 | 0 | 1 | 0 | 0 | 36 | 275 | 0 | 0 |
| PE | 20601 | 100 | 12 | 5 | 1 | 2 | 3 | 37 | 654 | 3 | 0 |
| PI | 10198 | 13 | 3 | 1 | 3 | 0 | 0 | 0 | 7 | 0 | 0 |
| PR | 27118 | 21 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| RJ | 34179 | 176 | 18 | 110 | 97 | 90 | 10 | 190 | 2781 | 9 | 15 |
| RN | 7594 | 21 | 4 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| RO | 4687 | 9 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| RR | 1510 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| RS | 27523 | 15 | 3 | 2 | 0 | 0 | 1 | 1 | 2 | 0 | 0 |
| SC | 17070 | 8 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| SE | 5859 | 9 | 1 | 0 | 0 | 1 | 0 | 2 | 51 | 0 | 0 |
| SP | 101210 | 472 | 100 | 112 | 86 | 18 | 3 | 84 | 1567 | 4 | 0 |
| TO | 4380 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ZZ | 1207 | 67 | 4 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |

</details>

![Acumulado](fig_acumulado.png)

## 2. Resultado oficial × simulações excluindo seções encerradas depois de cada horário

Cada simulação **remove inteiramente** as seções cujo encerramento foi no horário de corte ou depois (resolução de minuto). Seções sem horário no BU permanecem em todos os cenários.

|  | todas as urnas | corte 17:30 | corte 18:00 | corte 18:30 | corte 19:00 |
|---|---:|---:|---:|---:|---:|
| votos LULA | 63.534.706 | 62.355.426 | 62.434.560 | 62.481.171 | 62.545.394 |
| votos FLAVIO BOLSONARO | 59.152.992 | 58.200.833 | 58.256.974 | 58.291.718 | 58.349.053 |
| % válidos LULA | 51.786 | 51.723 | 51.731 | 51.734 | 51.736 |
| % válidos FLAVIO BOLSONARO | 48.214 | 48.277 | 48.269 | 48.266 | 48.264 |
| margem (votos) | +4.381.714 | +4.154.593 | +4.177.586 | +4.189.453 | +4.196.341 |
| margem (p.p.) | +3.571 | +3.446 | +3.461 | +3.469 | +3.471 |
| vencedor | LULA (13) | LULA (13) | LULA (13) | LULA (13) | LULA (13) |
| vencedor muda? | — | não | não | não | não |
| seções excluídas | 0 | 7.615 | 7.087 | 6.771 | 6.350 |
| eleitores aptos excluídos | 0 | 2.745.591 | 2.569.774 | 2.464.661 | 2.308.053 |
| comparecimento excluído | 0 | 2.210.855 | 2.070.610 | 1.986.312 | 1.860.564 |
| votos LULA excluídos | 0 | 1.179.280 | 1.100.146 | 1.053.535 | 989.312 |
| votos FLAVIO BOLSONARO excluídos | 0 | 952.159 | 896.018 | 861.274 | 803.939 |

Oficial TSE: LULA 64.256.232, FLAVIO BOLSONARO 59.826.041 — diferença para “todas as urnas”: -721526 / -673049.

Composição dos votos nas seções excluídas (só as seções tardias):

| seções | n | % válidos LULA | % válidos FLAVIO BOLSONARO |
|---|---:|---:|---:|
| depois de 17:30 | 7.615 | 55.33 | 44.67 |
| depois de 18:00 | 7.087 | 55.11 | 44.89 |
| depois de 18:30 | 6.771 | 55.02 | 44.98 |
| depois de 19:00 | 6.350 | 55.17 | 44.83 |

## 3. Onde estão as seções tardias

### Por UF

| UF | seções | ≥17:30 (n) | ≥17:30 (% UF) | ≥18:00 (n) | ≥18:00 (% UF) | ≥18:00 (% do total BR) | ≥19:00 (n) | ≥19:00 (% do total BR) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RJ | 37.675 | 3.320 | 8.81 | 3.192 | 8.47 | 45.04 | 2.805 | 44.17 |
| SP | 103.656 | 1.974 | 1.90 | 1.762 | 1.70 | 24.86 | 1.571 | 24.74 |
| BA | 34.952 | 1.047 | 3.00 | 992 | 2.84 | 14.00 | 934 | 14.71 |
| PE | 21.418 | 717 | 3.35 | 700 | 3.27 | 9.88 | 657 | 10.35 |
| PB | 10.662 | 316 | 2.96 | 312 | 2.93 | 4.40 | 275 | 4.33 |
| SE | 5.923 | 55 | 0.93 | 54 | 0.91 | 0.76 | 51 | 0.80 |
| DF | 6.955 | 33 | 0.47 | 17 | 0.24 | 0.24 | 17 | 0.27 |
| PI | 10.225 | 14 | 0.14 | 10 | 0.10 | 0.14 | 7 | 0.11 |
| PA | 20.827 | 19 | 0.09 | 9 | 0.04 | 0.13 | 8 | 0.13 |
| MT | 8.287 | 13 | 0.16 | 9 | 0.11 | 0.13 | 9 | 0.14 |
| MA | 17.586 | 17 | 0.10 | 4 | 0.02 | 0.06 | 3 | 0.05 |
| MG | 49.086 | 17 | 0.03 | 4 | 0.01 | 0.06 | 1 | 0.02 |
| RS | 27.547 | 9 | 0.03 | 4 | 0.01 | 0.06 | 2 | 0.03 |
| RN | 7.622 | 7 | 0.09 | 3 | 0.04 | 0.04 | 3 | 0.05 |
| ZZ | 1.281 | 7 | 0.55 | 3 | 0.23 | 0.04 | 0 | 0.00 |
| GO | 15.441 | 5 | 0.03 | 2 | 0.01 | 0.03 | 1 | 0.02 |
| ES | 9.844 | 4 | 0.04 | 2 | 0.02 | 0.03 | 2 | 0.03 |
| AL | 7.101 | 7 | 0.10 | 2 | 0.03 | 0.03 | 2 | 0.03 |
| AC | 2.270 | 1 | 0.04 | 1 | 0.04 | 0.01 | 1 | 0.02 |
| CE | 23.765 | 14 | 0.06 | 1 | 0.00 | 0.01 | 0 | 0.00 |
| RO | 4.698 | 2 | 0.04 | 1 | 0.02 | 0.01 | 0 | 0.00 |
| SC | 17.081 | 3 | 0.02 | 1 | 0.01 | 0.01 | 0 | 0.00 |
| AM | 7.907 | 9 | 0.11 | 1 | 0.01 | 0.01 | 0 | 0.00 |
| PR | 27.142 | 3 | 0.01 | 1 | 0.00 | 0.01 | 1 | 0.02 |
| MS | 6.861 | 1 | 0.01 | 0 | 0.00 | 0.00 | 0 | 0.00 |
| AP | 1.914 | 1 | 0.05 | 0 | 0.00 | 0.00 | 0 | 0.00 |
| RR | 1.519 | 0 | 0.00 | 0 | 0.00 | 0.00 | 0 | 0.00 |
| TO | 4.384 | 0 | 0.00 | 0 | 0.00 | 0.00 | 0 | 0.00 |

### 30 municípios com mais seções encerradas às 18:00 ou depois

| Município | UF | seções | ≥18:00 (n) | ≥18:00 (% mun.) | ≥19:00 (n) | último encerramento |
|---|---:|---:|---:|---:|---:|---:|
| RIO DE JANEIRO | RJ | 12.635 | 2.149 | 17.0 | 1.978 | 19:57 |
| SÃO PAULO | SP | 26.683 | 1.661 | 6.2 | 1.481 | 19:18 |
| SALVADOR | BA | 4.871 | 753 | 15.5 | 728 | 19:21 |
| PETRÓPOLIS | RJ | 804 | 297 | 36.9 | 285 | 19:07 |
| JOÃO PESSOA | PB | 1.706 | 293 | 17.2 | 265 | 19:10 |
| NITERÓI | RJ | 1.327 | 244 | 18.4 | 68 | 19:08 |
| ITABORAÍ | RJ | 540 | 241 | 44.6 | 237 | 19:09 |
| RECIFE | PE | 3.481 | 229 | 6.6 | 220 | 19:07 |
| SÃO GONÇALO | RJ | 2.019 | 112 | 5.5 | 108 | 19:14 |
| FEIRA DE SANTANA | BA | 1.218 | 61 | 5.0 | 55 | 19:07 |
| JABOATÃO DOS GUARARAPES | PE | 1.342 | 52 | 3.9 | 49 | 19:20 |
| PASSIRA | PE | 79 | 49 | 62.0 | 46 | 19:09 |
| OLINDA | PE | 893 | 48 | 5.4 | 47 | 19:05 |
| LAURO DE FREITAS | BA | 413 | 45 | 10.9 | 40 | 19:05 |
| ARACAJU | SE | 1.354 | 42 | 3.1 | 40 | 19:05 |
| CABO DE SANTO AGOSTINHO | PE | 496 | 41 | 8.3 | 37 | 19:05 |
| PAULISTA | PE | 661 | 34 | 5.1 | 34 | 19:10 |
| CUMARU | PE | 49 | 32 | 65.3 | 32 | 19:04 |
| CARUARU | PE | 708 | 32 | 4.5 | 24 | 19:06 |
| MAGÉ | RJ | 621 | 30 | 4.8 | 26 | 19:04 |
| SANTA TEREZINHA | PE | 28 | 28 | 100.0 | 25 | 19:06 |
| VITÓRIA DE SANTO ANTÃO | PE | 309 | 23 | 7.4 | 23 | 19:05 |
| QUEIMADOS | RJ | 326 | 23 | 7.1 | 20 | 19:09 |
| GARANHUNS | PE | 292 | 21 | 7.2 | 20 | 19:05 |
| ITAPETIM | PE | 38 | 20 | 52.6 | 20 | 19:03 |
| VOLTA REDONDA | RJ | 705 | 20 | 2.8 | 20 | 19:47 |
| ENCRUZILHADA | BA | 55 | 20 | 36.4 | 18 | 19:05 |
| CUBATÃO | SP | 303 | 20 | 6.6 | 16 | 19:06 |
| EMBU DAS ARTES | SP | 634 | 19 | 3.0 | 16 | 19:04 |
| BREJINHO | PE | 23 | 18 | 78.3 | 17 | 19:03 |

## 4. Seções com problema (`flag_problema`)

`flag_problema` é uma máscara de bits; uma seção pode ter mais de um. Nenhuma seção foi descartada em silêncio: seções sem BU/sem votos ficam no parquet com campos nulos e **não entram** em nenhum cenário (não há votos para somar); seções sem horário entram em todos os cenários.

| bit | descrição | seções | aptos | comparecimento |
|---|---:|---:|---:|---:|
| 1 | sem aux.json | 5.132 | 0 | 0 |
| 2 | sem BU | 487 | 0 | 0 |
| 4 | erro ao decodificar BU | 0 | 0 | 0 |
| 8 | sem horário de encerramento | 0 | 0 | 0 |
| 16 | urna não ordinária (contingência) | 5.678 | 1.834.919 | 1.474.506 |
| 32 | BU não é de votação em urna (SA/manual) | 16 | 4.953 | 3.829 |
| 64 | mais de um BU publicado | 0 | 0 | 0 |
| 128 | BU sem o cargo | 0 | 0 | 0 |
| 256 | horário de encerramento atípico | 0 | 0 | 0 |
| 512 | votos fora dos 2 candidatos | 0 | 0 | 0 |
| 1024 | fuso não inferido (padrão UF) | 0 | 0 | 0 |
| — | **qualquer flag** | 11.311 | 1.839.191 | 1.477.772 |

Combinações tipoUrna/tipoArquivo encontradas nos BUs: {'1/1': 487937, '4/1': 5676, 'None/None': 5619, '1/2': 14, '6/2': 2}.

## 5. Fuso horário

O relógio da urna grava **hora local**. Como as urnas abrem às 8h de Brasília no país todo, o fuso de cada município foi inferido pela **moda de (8h − hora local de abertura)** entre as seções que abriram até HH:30, e conferido contra o padrão da UF (AC +2h; AM, RO, RR, MT, MS +1h; demais 0; sem horário de verão em 2026). Somado esse deslocamento, todos os horários do relatório estão em **Brasília**.

| UF | padrão | municípios por deslocamento inferido | divergentes | exemplos de divergentes |
|---|---:|---:|---:|---:|
| AC | +2h | +2h: 22 | 0 | — |
| AL | +0h | +0h: 102 | 0 | — |
| AM | +1h | +1h: 51, +2h: 11 | 11 | 02313 (+2h), TABATINGA (+2h), 02291 (+2h), 02399 (+2h), 02135 (+2h), 02496 (+2h), 02054 (+2h), 02917 (+2h), 02020 (+2h), ITAMARATI (+2h), 02755 (+2h) |
| AP | +0h | +0h: 16 | 0 | — |
| BA | +0h | +0h: 416 | 0 | — |
| CE | +0h | +0h: 184 | 0 | — |
| DF | +0h | +0h: 1 | 0 | — |
| ES | +0h | +0h: 78 | 0 | — |
| GO | +0h | +0h: 245 | 0 | — |
| MA | +0h | +0h: 217 | 0 | — |
| MG | +0h | +0h: 837 | 0 | — |
| MS | +1h | +1h: 79 | 0 | — |
| MT | +1h | +1h: 142 | 0 | — |
| PA | +0h | +0h: 144 | 0 | — |
| PB | +0h | +0h: 223 | 0 | — |
| PE | +0h | -1h: 1, +0h: 184 | 1 | FERNANDO DE NORONHA (-1h) |
| PI | +0h | +0h: 224 | 0 | — |
| PR | +0h | +0h: 399 | 0 | — |
| RJ | +0h | +0h: 92 | 0 | — |
| RN | +0h | +0h: 159 | 0 | — |
| RO | +1h | +1h: 52 | 0 | — |
| RR | +1h | +1h: 15 | 0 | — |
| RS | +0h | +0h: 497 | 0 | — |
| SC | +0h | +0h: 295 | 0 | — |
| SE | +0h | +0h: 75 | 0 | — |
| SP | +0h | +0h: 645 | 0 | — |
| TO | +0h | +0h: 139 | 0 | — |
| ZZ | +0h | +0h: 117 | 0 | — |

No exterior (ZZ) as urnas abrem às 8h **locais**; o mesmo método converte o horário para a “hora de Brasília equivalente” ao calendário local de votação (encerramento normal ≈ 17:00), e não para o instante real em Brasília. A prorrogação até 19h (Brasília) não se aplica ao exterior.

## Método

1. `ele-c.json` → pleito e eleição do 2º turno (25/10/2026) que contém o cargo.
2. `…/arquivo-urna/<pleito>/config/<uf>/<uf>-p<pleito>-cs.json` → lista de seções (entradas com `nsp` são seções
   agregadas, sem BU próprio).
3. Por seção: `…-aux.json` → nome e diretório (hash) do `-bu.dat`; baixa só o BU (≈0,8–1 KB), em memória.
   `.imgbu` não está publicado em 2026 (404 em 100% da amostra); `.logjez`/`.rdv` não são baixados.
4. Decodificação DER do `EntidadeEnvelopeGenerico` → `EntidadeBoletimUrna` (estrutura do `bu.asn1` da
   Documentação Técnica do TSE, conferida em BUs reais): `dadosSecao.dataHoraEncerramento`, `qtdEleitoresAptos`,
   `qtdComparecimento` e votos por tipo (nominal/branco/nulo) do cargo.
5. Nada bruto é gravado: o checkpoint guarda só os campos extraídos.
6. **Não** foram usados `dt/ht/dg/hg` dos JSON de resultado nem `da/ha` do cs.json (são horários de
   recebimento/totalização).

## Limitações

- **Fechar depois das 17h não é prova de prorrogação.** Pela lei, quem está na fila às 17h vota; urnas com
  fila longa encerram legitimamente depois das 17h. As simulações só mostram quanto pesam as seções tardias,
  sem distinguir fila legítima de prorrogação.
- Excluir uma seção inteira remove também quem votou antes das 17h nela; é um cenário extremo, não uma estimativa
  de “votos fora do horário”.
- **Fuso:** horários convertidos de hora local por inferência (moda da abertura por município). Municípios sem
  abertura válida usam o padrão da UF (flag 1024). Exterior: ver seção 5.
- `dataHoraEncerramento` é o relógio interno da urna (ajustado na carga); pequenas imprecisões de relógio são possíveis.
- Resolução de minuto: 17:30:xx conta como “17:30 ou depois”.
- Seções com problema (seção 4) estão contadas; seções sem BU não entram nos votos — veja a validação contra o
  oficial para o tamanho do efeito.
- O hash do diretório no `aux.json` não é um SHA simples do BU; a integridade não foi verificada por hash/assinatura
  (custo alto); a validação é feita pela soma contra a totalização oficial.

