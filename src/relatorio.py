"""Junta os parquets por UF, valida contra o total oficial e gera relatorio.md + PNGs.

Uso: python src/relatorio.py --entrada out --cargo 1
"""
import argparse
import asyncio
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(__file__))
import coleta as C  # noqa: E402
import tse  # noqa: E402

CORTES = [("17:30", 17 * 60 + 30), ("18:00", 18 * 60), ("18:30", 18 * 60 + 30), ("19:00", 19 * 60)]
FAIXAS = ["até 17:30", "17:30–18:00", "18:00–18:30", "18:30–19:00", "depois de 19:00"]
AZUL, LARANJA, CINZA, TINTA, TINTA2 = "#2a78d6", "#eb6834", "#8a8984", "#0b0b0b", "#52514e"


def hhmm(m):
    return f"{int(m) // 60:02d}:{int(m) % 60:02d}"


def pct(a, b):
    return 100.0 * a / b if b else float("nan")


def f1(x):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.1f}"


def f2(x):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.2f}"


def n(x):
    return f"{int(x):,}".replace(",", ".")


def faixa(h):
    """Faixa de fechamento. 'até 17:30' = encerrou antes de 17:30:00 (resolução de minuto)."""
    edges = [c for _, c in CORTES]
    out = np.full(len(h), "sem horário", dtype=object)
    ok = h.notna()
    idx = np.searchsorted(edges, h[ok].astype(int).to_numpy(), side="right")
    out[ok.to_numpy()] = np.array(FAIXAS, dtype=object)[idx]
    return out


def md_table(df, index=True):
    cols = ([df.index.name or ""] if index else []) + [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] + ["---:"] * (len(cols) - 1)) + "|"]
    for i, row in df.iterrows():
        vals = ([str(i)] if index else []) + [str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def distribuicao(df, peso=None):
    """% por faixa e % acumulado por UF + Brasil (só seções com horário)."""
    d = df[df.hora_fechamento.notna()].copy()
    d["faixa"] = faixa(d.hora_fechamento)
    w = d[peso] if peso else pd.Series(1, index=d.index)
    d["w"] = w.fillna(0)
    piv = d.pivot_table(index="uf", columns="faixa", values="w", aggfunc="sum", fill_value=0, observed=True)
    piv = piv.reindex(columns=FAIXAS, fill_value=0)
    piv.loc["BRASIL"] = piv.sum()
    tot = piv.sum(axis=1)
    por = piv.div(tot, axis=0) * 100
    acum = por.cumsum(axis=1)
    acum.columns = ["até 17:30", "até 18:00", "até 18:30", "até 19:00", "todas (inclui >19:00)"]
    return piv, por, acum, tot


def cenario(df, corte, c1, c2):
    if corte is None:
        keep = pd.Series(True, index=df.index)
    else:
        keep = df.hora_fechamento.isna() | (df.hora_fechamento < corte)
    k, x = df[keep], df[~keep]
    v1, v2 = int(k.votos_cand1.sum()), int(k.votos_cand2.sum())
    val = v1 + v2
    p1, p2 = pct(v1, val), pct(v2, val)
    ven = c1 if v1 > v2 else c2 if v2 > v1 else "empate"
    return {"v1": v1, "v2": v2, "p1": p1, "p2": p2, "margem_votos": v1 - v2, "margem_pp": p1 - p2,
            "vencedor": ven, "brancos": int(k.brancos.sum()), "nulos": int(k.nulos.sum()),
            "secoes_excl": len(x), "aptos_excl": int(x.aptos.fillna(0).sum()),
            "comp_excl": int(x.comparecimento.fillna(0).sum()),
            "v1_excl": int(x.votos_cand1.fillna(0).sum()), "v2_excl": int(x.votos_cand2.fillna(0).sum())}


def graficos(df, base, titulo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#c9c8c2", "axes.labelcolor": TINTA2,
                         "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.spines.top": False,
                         "axes.spines.right": False, "font.family": "DejaVu Sans"})
    d = df[df.hora_fechamento.notna()]
    h = d.hora_fechamento.astype(int)
    edges = list(range(17 * 60, 19 * 60 + 31, 15))
    labels = ["<17:00"] + [f"{hhmm(a)}–{hhmm(b)}" for a, b in zip(edges[:-1], edges[1:])] + ["≥19:30"]
    idx = np.searchsorted(edges, h.to_numpy(), side="right")
    cnt = np.bincount(idx, minlength=len(labels))
    cmp_ = np.bincount(idx, weights=d.comparecimento.fillna(0).to_numpy(), minlength=len(labels))
    ps, pc = 100 * cnt / cnt.sum(), 100 * cmp_ / cmp_.sum()

    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=130)
    x = np.arange(len(labels))
    wdt = 0.38
    imax = int(np.argmax(ps))
    teto = max(1.0, 1.3 * max(np.delete(np.maximum(ps, pc), imax)))  # barra dominante truncada
    ax.bar(x - wdt / 2 - 0.01, np.minimum(ps, teto), wdt, color=AZUL, label="% das seções")
    ax.bar(x + wdt / 2 + 0.01, np.minimum(pc, teto), wdt, color=LARANJA, label="% do comparecimento")
    for xi, v in zip(x, ps):
        if v > 0 and xi != imax:
            ax.text(xi - wdt / 2, v + teto * 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5, color=TINTA2)
    ax.annotate(f"← {labels[imax]}: {ps[imax]:.1f}% das seções, {pc[imax]:.1f}% do comparecimento (barra truncada)",
                (imax + wdt + 0.1, teto * 0.93), fontsize=8.5, color=TINTA, ha="left", va="center")
    ax.set_xticks(x, labels, rotation=35, ha="right")
    ax.set_ylabel("% (barra mais alta truncada)")
    ax.set_ylim(0, teto)
    ax.grid(axis="y", color="#e6e5e0", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title(f"{titulo}: horário de encerramento das urnas (Brasília), faixas de 15 min",
                 loc="left", color=TINTA, fontsize=11)
    fig.tight_layout()
    fig.savefig(f"{base}_histograma.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=130)
    grid = np.arange(16 * 60 + 45, 20 * 60 + 1)
    hs = np.sort(h.to_numpy())
    order = np.argsort(h.to_numpy())
    wc = np.cumsum(d.comparecimento.fillna(0).to_numpy()[order])
    ys = 100 * np.searchsorted(hs, grid, side="left") / len(hs)
    yc = 100 * np.concatenate([[0], wc])[np.searchsorted(hs, grid, side="left")] / wc[-1]
    ax.plot(grid, ys, color=AZUL, lw=2, label="seções")
    ax.plot(grid, yc, color=LARANJA, lw=2, label="comparecimento")
    y0 = max(0, np.floor(min(ys[grid == 17 * 60 + 15][0], yc[grid == 17 * 60 + 15][0]) / 5) * 5 - 5)
    ax.set_ylim(y0, 100.5)
    for nome, c in CORTES:
        ax.axvline(c, color=CINZA, lw=0.8, ls=(0, (3, 3)))
        yv = 100 * np.searchsorted(hs, c, side="left") / len(hs)
        ax.annotate(f"{nome}\n{yv:.2f}%", (c, y0 + (100 - y0) * 0.03), fontsize=8, color=TINTA2, ha="left", xytext=(3, 0),
                    textcoords="offset points")
    ax.set_xticks(range(17 * 60, 20 * 60 + 1, 30), [hhmm(m) for m in range(17 * 60, 20 * 60 + 1, 30)])
    ax.set_ylabel("% acumulado encerrado (eixo com zoom)")
    ax.grid(color="#e6e5e0", linewidth=0.6)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title(f"{titulo}: % acumulado de urnas encerradas até cada horário (Brasília)",
                 loc="left", color=TINTA, fontsize=11)
    fig.tight_layout()
    fig.savefig(f"{base}_acumulado.png")
    plt.close(fig)
    return labels, cnt, cmp_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default="out")
    ap.add_argument("--cargo", type=int, default=1)
    ap.add_argument("--ufs-esperadas", default="")
    ap.add_argument("--saida-md", default="")
    a = ap.parse_args()
    cargo = a.cargo
    arqs = sorted(glob.glob(os.path.join(a.entrada, "**", f"secoes_{cargo}_*.parquet"), recursive=True))
    metas = {}
    for m in glob.glob(os.path.join(a.entrada, "**", f"meta_{cargo}_*.json"), recursive=True):
        j = json.load(open(m))
        metas[j["uf"]] = j
    if not arqs:
        raise SystemExit("nenhum parquet encontrado")
    tab = pa.concat_tables([pq.read_table(f) for f in arqs], promote_options="permissive")
    tab = tab.combine_chunks()
    tab = tab.set_column(0, "uf", tab.column("uf").cast(pa.string()).dictionary_encode())
    meta0 = next(iter(metas.values()))
    slug = meta0.get("cargo_nome", str(cargo)).lower().replace(" ", "_")
    os.makedirs("dados", exist_ok=True)
    pq.write_table(tab, f"dados/secoes_{slug}.parquet", compression="zstd", compression_level=19)
    df = tab.to_pandas()
    df["uf"] = df["uf"].astype(str)
    for c in ("hora_fechamento",):
        df[c] = df[c].astype("Int64")
    (n1, c1), (n2, c2) = meta0["candidatos"]
    c1s, c2s = f"{c1} ({n1})", f"{c2} ({n2})"
    ufs_presentes = sorted(metas)
    esperadas = list(tse.UFS) if a.ufs_esperadas == "todas" else ([u for u in a.ufs_esperadas.split(",") if u] or ufs_presentes)
    faltando = sorted(set(esperadas) - set(ufs_presentes))
    brasil_completo = not faltando and len(set(esperadas)) == len(tse.UFS)

    # oficial Brasil (ou soma das UFs presentes)
    of_br = None
    if brasil_completo:
        async def _br():
            cli = tse.Cliente(4)
            try:
                return tse.resumo_oficial(await cli.json(tse.url_oficial(meta0["eleicao"], "br", cargo)))
            finally:
                await cli.fechar()
        try:
            of_br = asyncio.run(_br())
        except Exception as e:  # noqa: BLE001
            print("aviso: oficial BR indisponível", e)

    L = []
    titulo = f"{meta0['eleicao_nome']} — {meta0.get('cargo_nome', cargo)}"
    L.append(f"# Horário de encerramento das urnas e simulações de corte — {titulo}\n")
    L.append(f"Eleição {meta0['eleicao']} (pleito {meta0['pleito']}), 25/10/2026. "
             f"UFs no relatório: {len(ufs_presentes)} ({', '.join(u.upper() for u in ufs_presentes)}).")
    if faltando:
        L.append(f"\n> **Atenção: faltam UFs** {', '.join(u.upper() for u in faltando)} — os números de Brasil "
                 f"abaixo cobrem só as UFs presentes.")
    L.append("\nFonte: Boletins de Urna (arquivo `-bu.dat`, ASN.1/DER) publicados em resultados.tse.jus.br, "
             "campo `dataHoraEncerramento` do BU, normalizado para o horário de Brasília. Detalhes de método e "
             "limitações no fim do documento. Dados por seção em `dados/secoes_*.parquet`.\n")

    # ---------- resumo
    tot_sec = len(df)
    com_hora = int(df.hora_fechamento.notna().sum())
    piv_s, por_s, acum_s, tot_s = distribuicao(df)
    piv_c, por_c, acum_c, tot_c = distribuicao(df, "comparecimento")
    cen = {None: cenario(df, None, c1s, c2s)}
    for nome, c in CORTES:
        cen[c] = cenario(df, c, c1s, c2s)

    L.append("## Resumo\n")
    n_nao_inst = int(((df.flag_problema & C.F_NAO_INSTALADA) > 0).sum())
    L.append(f"- Seções (exceto agregadas): **{n(tot_sec)}**, das quais {n(n_nao_inst)} não instaladas; com horário "
             f"de encerramento: **{n(com_hora)}**; seções agregadas (votos no BU da seção principal): "
             f"{n(sum(m['n_agregadas'] for m in metas.values()))}.")
    hh = df.hora_fechamento.dropna().astype(int)
    pico = ((hh >= 19 * 60) & (hh < 19 * 60 + 15)).sum()
    meio = ((hh >= 17 * 60 + 30) & (hh < 19 * 60)).sum()
    L.append(f"- Formato da distribuição: {f2(pct(((hh >= 17 * 60) & (hh < 17 * 60 + 15)).sum(), len(hh)))}% das "
             f"seções encerraram entre 17:00 e 17:15; entre 17:30 e 19:00 encerraram só {n(meio)} seções, e há um "
             f"**segundo pico entre 19:00 e 19:15** ({n(pico)} seções, {f2(pct(pico, len(hh)))}%), compatível com "
             f"encerramento coordenado às 19h nos locais com prorrogação (ver seção 3).")
    b = acum_s.loc["BRASIL"]
    L.append(f"- Urnas encerradas (Brasil, % das seções): até 17:30 **{f2(b.iloc[0])}%**, até 18:00 "
             f"**{f2(b.iloc[1])}%**, até 18:30 **{f2(b.iloc[2])}%**, até 19:00 **{f2(b.iloc[3])}%**; "
             f"depois das 19:00: **{f2(por_s.loc['BRASIL'].iloc[4])}%** ({n(piv_s.loc['BRASIL'].iloc[4])} seções).")
    muda = [nome for nome, c in CORTES if cen[c]["vencedor"] != cen[None]["vencedor"]]
    L.append(f"- Vencedor com todas as urnas: **{cen[None]['vencedor']}** "
             f"({f2(max(cen[None]['p1'], cen[None]['p2']))}% dos válidos, margem {n(abs(cen[None]['margem_votos']))} votos). "
             + ("**O vencedor muda** nos cortes: " + ", ".join(muda) + "." if muda else
                "**O vencedor não muda** em nenhum dos 4 cortes."))
    L.append("")

    # ---------- validação
    L.append("## Validação: soma dos BUs × resultado oficial do TSE\n")
    rows = []
    soma = df.groupby("uf")[["votos_cand1", "votos_cand2", "brancos", "nulos", "comparecimento"]].sum()
    for uf in ufs_presentes:
        o = metas[uf].get("oficial") or {}
        oc = o.get("cands", {})
        s = soma.loc[uf.upper()] if uf.upper() in soma.index else None
        if s is None:
            continue
        ov = [oc.get(str(n1), {}).get("vap"), oc.get(str(n2), {}).get("vap"), o.get("brancos"), o.get("nulos"),
              o.get("comparecimento")]
        sv = [int(s.votos_cand1), int(s.votos_cand2), int(s.brancos), int(s.nulos), int(s.comparecimento)]
        dif = [(x - y) if y is not None else None for x, y in zip(sv, ov)]
        rows.append([uf.upper()] + [n(x) for x in sv] + [", ".join("—" if d is None else f"{d:+d}" for d in dif)])
    vt = pd.DataFrame(rows, columns=["UF", c1, c2, "brancos", "nulos", "comparec.",
                                     f"diferença BU−oficial ({c1}, {c2}, br, nu, comp)"]).set_index("UF")
    tot_bu = [int(soma.votos_cand1.sum()), int(soma.votos_cand2.sum()), int(soma.brancos.sum()),
              int(soma.nulos.sum()), int(soma.comparecimento.sum())]
    if of_br:
        ov = [of_br["cands"].get(n1, {}).get("vap"), of_br["cands"].get(n2, {}).get("vap"), of_br["brancos"],
              of_br["nulos"], of_br["comparecimento"]]
        L.append(f"Oficial TSE Brasil (totalização de {of_br['dt_totalizacao']}; seções totalizadas "
                 f"{of_br['secoes_totalizadas']} de {of_br['secoes_total']}):\n")
        bt = pd.DataFrame([[n(x) for x in tot_bu], [n(x) if x is not None else "—" for x in ov],
                           [f"{x - y:+d}" if y is not None else "—" for x, y in zip(tot_bu, ov)]],
                          index=pd.Index(["soma dos BUs", "oficial TSE", "diferença"], name="Brasil"),
                          columns=[c1, c2, "brancos", "nulos", "comparecimento"])
        L.append(md_table(bt) + "\n")
        ok = all(y is not None and x == y for x, y in zip(tot_bu[:2], ov[:2]))
        L.append("**Bate exatamente com o oficial** (votos dos candidatos)." if ok else
                 "**Não bate exatamente** — ver diferença acima e seções com problema abaixo.")
        L.append("")
    if len(ufs_presentes) <= 3:
        L.append("Por UF:\n\n" + md_table(vt) + "\n")
    else:
        L.append("<details><summary>Por UF</summary>\n\n" + md_table(vt) + "\n\n</details>\n")

    # ---------- distribuição
    L.append("## 1. Percentual de urnas encerradas por horário (Brasília)\n")
    L.append("Faixas: “até 17:30” = encerramento antes de 17:30:00; “17:30–18:00” = de 17:30:00 a 17:59:59; etc. "
             "Só seções com horário de encerramento no BU.\n")
    br = pd.DataFrame({"seções": [n(x) for x in piv_s.loc["BRASIL"]],
                       "% seções": [f2(x) for x in por_s.loc["BRASIL"]],
                       "% seções acum.": [f2(x) for x in acum_s.loc["BRASIL"]],
                       "comparecimento": [n(x) for x in piv_c.loc["BRASIL"]],
                       "% comparec.": [f2(x) for x in por_c.loc["BRASIL"]],
                       "% comparec. acum.": [f2(x) for x in acum_c.loc["BRASIL"]]},
                      index=pd.Index(FAIXAS, name="Brasil"))
    L.append(md_table(br) + "\n")
    ordem = [u for u in por_s.index if u != "BRASIL"]
    ordem = sorted(ordem, key=lambda u: -por_s.loc[u].iloc[1:].sum()) + ["BRASIL"]

    def tabuf(t, extra=None):
        t = t.loc[ordem].map(f2)
        if extra is not None:
            t.insert(0, "seções", extra.loc[ordem].map(n))
        t.index.name = "UF"
        return md_table(t)
    L.append("### Por UF — % das seções em cada faixa (ordenado pela % que fechou depois de 17:30)\n")
    L.append(tabuf(por_s, tot_s) + "\n")
    L.append("### Por UF — % acumulado das seções\n")
    L.append(tabuf(acum_s) + "\n")
    L.append("<details><summary>Por UF — ponderado por comparecimento (por faixa e acumulado)</summary>\n\n"
             + tabuf(por_c) + "\n\n" + tabuf(acum_c) + "\n\n</details>\n")

    # ---------- histograma
    base = "fig" if cargo == 1 else f"fig_{slug}"
    labels, cnt, cmp_ = graficos(df, base, f"2º turno 2026 — {meta0.get('cargo_nome', cargo)}")
    L.append("## Histograma de encerramento (faixas de 15 min)\n")
    L.append(f"![Histograma]({base}_histograma.png)\n")
    hist = pd.DataFrame({"seções": [n(x) for x in cnt], "% seções": [f2(x) for x in 100 * cnt / cnt.sum()],
                         "comparecimento": [n(x) for x in cmp_], "% comparec.": [f2(x) for x in 100 * cmp_ / cmp_.sum()]},
                        index=pd.Index(labels, name="faixa (Brasília)"))
    L.append(md_table(hist) + "\n")
    d = df[df.hora_fechamento.notna()]
    idx = np.searchsorted(list(range(17 * 60, 19 * 60 + 31, 15)), d.hora_fechamento.astype(int).to_numpy(), side="right")
    hu = pd.crosstab(d.uf, pd.Categorical(np.array(labels)[idx], categories=labels))
    hu.index.name = "UF"
    L.append("<details><summary>Histograma por UF (nº de seções)</summary>\n\n" + md_table(hu) + "\n\n</details>\n")
    L.append(f"![Acumulado]({base}_acumulado.png)\n")

    # ---------- cenários
    L.append("## 2. Resultado oficial × simulações excluindo seções encerradas depois de cada horário\n")
    L.append("Cada simulação **remove inteiramente** as seções cujo encerramento foi no horário de corte ou depois "
             "(resolução de minuto). Seções sem horário no BU permanecem em todos os cenários.\n")
    cols = ["todas as urnas"] + [f"corte {nm}" for nm, _ in CORTES]
    keys = [None] + [c for _, c in CORTES]
    linhas = {
        f"votos {c1}": [n(cen[k]["v1"]) for k in keys],
        f"votos {c2}": [n(cen[k]["v2"]) for k in keys],
        f"% válidos {c1}": [f"{cen[k]['p1']:.3f}" for k in keys],
        f"% válidos {c2}": [f"{cen[k]['p2']:.3f}" for k in keys],
        "margem (votos)": [f"{cen[k]['margem_votos']:+,}".replace(",", ".") for k in keys],
        "margem (p.p.)": [f"{cen[k]['margem_pp']:+.3f}" for k in keys],
        "vencedor": [cen[k]["vencedor"] for k in keys],
        "vencedor muda?": ["—"] + ["**SIM**" if cen[k]["vencedor"] != cen[None]["vencedor"] else "não" for k in keys[1:]],
        "seções excluídas": [n(cen[k]["secoes_excl"]) for k in keys],
        "eleitores aptos excluídos": [n(cen[k]["aptos_excl"]) for k in keys],
        "comparecimento excluído": [n(cen[k]["comp_excl"]) for k in keys],
        f"votos {c1} excluídos": [n(cen[k]["v1_excl"]) for k in keys],
        f"votos {c2} excluídos": [n(cen[k]["v2_excl"]) for k in keys],
    }
    ct = pd.DataFrame(linhas, index=cols).T
    ct.index.name = ""
    L.append(md_table(ct) + "\n")
    if of_br:
        L.append(f"Oficial TSE: {c1} {n(of_br['cands'][n1]['vap'])}, {c2} {n(of_br['cands'][n2]['vap'])} — "
                 f"diferença para “todas as urnas”: {cen[None]['v1'] - of_br['cands'][n1]['vap']:+d} / "
                 f"{cen[None]['v2'] - of_br['cands'][n2]['vap']:+d}.\n")
    # votos excluídos: quanto as seções tardias pendem
    L.append("Composição dos votos nas seções excluídas (só as seções tardias):\n")
    rr = []
    for nm, c in CORTES:
        x = cen[c]
        tv = x["v1_excl"] + x["v2_excl"]
        rr.append([f"depois de {nm}", n(x["secoes_excl"]), f2(pct(x["v1_excl"], tv)), f2(pct(x["v2_excl"], tv))])
    L.append(md_table(pd.DataFrame(rr, columns=["seções", "n", f"% válidos {c1}", f"% válidos {c2}"]).set_index("seções")) + "\n")

    # ---------- concentração
    L.append("## 3. Onde estão as seções tardias\n")
    nomes = {(m["uf"].upper(), int(k)): v for m in metas.values() for k, v in m["municipios"].items()}
    d = df[df.hora_fechamento.notna()].copy()
    for nm, c in CORTES[:2] + CORTES[3:]:
        d[f">= {nm}"] = d.hora_fechamento >= c
    gu = d.groupby("uf").agg(secoes=("secao", "size"), t1730=(">= 17:30", "sum"), t1800=(">= 18:00", "sum"),
                             t1900=(">= 19:00", "sum"))
    tt = gu[["t1730", "t1800", "t1900"]].sum()
    gu = gu.sort_values("t1800", ascending=False)
    cu = pd.DataFrame({
        "seções": gu.secoes.map(n),
        "≥17:30 (n)": gu.t1730.map(n), "≥17:30 (% UF)": (100 * gu.t1730 / gu.secoes).map(f2),
        "≥18:00 (n)": gu.t1800.map(n), "≥18:00 (% UF)": (100 * gu.t1800 / gu.secoes).map(f2),
        "≥18:00 (% do total BR)": (100 * gu.t1800 / max(tt.t1800, 1)).map(f2),
        "≥19:00 (n)": gu.t1900.map(n), "≥19:00 (% do total BR)": (100 * gu.t1900 / max(tt.t1900, 1)).map(f2)})
    cu.index.name = "UF"
    L.append("### Por UF\n\n" + md_table(cu) + "\n")
    gm = d.groupby(["uf", "mun"]).agg(secoes=("secao", "size"), t1800=(">= 18:00", "sum"),
                                      t1900=(">= 19:00", "sum"), ult=("hora_fechamento", "max")).reset_index()
    gm = gm[gm.t1800 > 0].sort_values(["t1800", "t1900"], ascending=False).head(30)
    gm["município"] = [nomes.get((u, int(m)), str(m)) for u, m in zip(gm.uf, gm.mun)]
    cm = pd.DataFrame({"UF": gm.uf, "seções": gm.secoes.map(n), "≥18:00 (n)": gm.t1800.map(n),
                       "≥18:00 (% mun.)": (100 * gm.t1800 / gm.secoes).map(f1), "≥19:00 (n)": gm.t1900.map(n),
                       "último encerramento": gm.ult.map(lambda m: hhmm(m))})
    cm.index = gm["município"]
    cm.index.name = "Município"
    L.append("### 30 municípios com mais seções encerradas às 18:00 ou depois\n\n" + md_table(cm) + "\n")

    # ---------- problemas
    L.append("## 4. Seções com problema (`flag_problema`)\n")
    L.append("`flag_problema` é uma máscara de bits; uma seção pode ter mais de um. Nenhuma seção foi descartada "
             "em silêncio: seções sem BU/sem votos ficam no parquet com campos nulos e **não entram** em nenhum "
             "cenário (não há votos para somar); seções sem horário entram em todos os cenários.\n")
    fr = []
    for bit, desc in C.FLAGS.items():
        m = (df.flag_problema & bit) > 0
        fr.append([f"{bit}", desc, n(m.sum()), n(df.loc[m, "aptos"].fillna(0).sum()),
                   n(df.loc[m, "comparecimento"].fillna(0).sum())])
    m = df.flag_problema > 0
    fr.append(["—", "**qualquer flag**", n(m.sum()), n(df.loc[m, "aptos"].fillna(0).sum()),
               n(df.loc[m, "comparecimento"].fillna(0).sum())])
    L.append(md_table(pd.DataFrame(fr, columns=["bit", "descrição", "seções", "aptos", "comparecimento"]), index=False) + "\n")
    tipos = {}
    for mm in metas.values():
        for k, v in mm.get("tipos_urna_arquivo", {}).items():
            tipos[k] = tipos.get(k, 0) + v
    L.append(f"Combinações tipoUrna/tipoArquivo encontradas nos BUs: {tipos}.\n")

    # ---------- fuso
    L.append("## 5. Fuso horário\n")
    L.append("O relógio da urna grava **hora local**. Como as urnas abrem às 8h de Brasília no país todo, o fuso de "
             "cada município foi inferido pela **moda de (8h − hora local de abertura)** entre as seções que abriram "
             "até HH:30, e conferido contra o padrão da UF (AC +2h; AM, RO, RR, MT, MS +1h; demais 0; sem horário "
             "de verão em 2026). Somado esse deslocamento, todos os horários do relatório estão em **Brasília**.\n")
    fz = []
    for uf in ufs_presentes:
        mm = metas[uf]
        div = mm.get("fuso_municipios_divergentes", {})
        nomesdiv = ", ".join(f"{mm['municipios'].get(str(int(k)), k)} ({v['h']:+d}h)" for k, v in list(div.items())[:15])
        fz.append([uf.upper(), f"{mm['fuso_padrao_uf_h']:+d}h",
                   ", ".join(f"{int(k):+d}h: {v}" for k, v in sorted(mm.get("fuso_resumo", {}).items())),
                   str(len(div)), nomesdiv or "—"])
    L.append(md_table(pd.DataFrame(fz, columns=["UF", "padrão", "municípios por deslocamento inferido",
                                                "divergentes", "exemplos de divergentes"]), index=False) + "\n")
    L.append("No exterior (ZZ) as urnas abrem às 8h **locais**; o mesmo método converte o horário para a "
             "“hora de Brasília equivalente” ao calendário local de votação (encerramento normal ≈ 17:00), e não "
             "para o instante real em Brasília. A prorrogação até 19h (Brasília) não se aplica ao exterior.\n")

    # ---------- método e limitações
    L.append("## Método\n")
    L.append("""1. `ele-c.json` → pleito e eleição do 2º turno (25/10/2026) que contém o cargo.
2. `…/arquivo-urna/<pleito>/config/<uf>/<uf>-p<pleito>-cs.json` → lista de seções (entradas com `nsp` são seções
   agregadas, sem BU próprio).
3. Por seção: `…-aux.json` → nome e diretório (hash) do `-bu.dat`; baixa só o BU (≈0,8–1 KB), em memória.
   Seções apuradas pelo Sistema de Apuração (cédula, sobretudo no exterior) não têm `-bu.dat`: usa-se o
   `-busa.dat` (mesmo formato), sem horário de encerramento de urna (flag 32 + 8).
   `.imgbu` não está publicado em 2026 (404 em 100% da amostra); `.logjez`/`.rdv` não são baixados.
4. Decodificação DER do `EntidadeEnvelopeGenerico` → `EntidadeBoletimUrna` (estrutura do `bu.asn1` da
   Documentação Técnica do TSE, conferida em BUs reais): `dadosSecao.dataHoraEncerramento`, `qtdEleitoresAptos`,
   `qtdComparecimento` e votos por tipo (nominal/branco/nulo) do cargo.
5. Nada bruto é gravado: o checkpoint guarda só os campos extraídos.
6. **Não** foram usados `dt/ht/dg/hg` dos JSON de resultado nem `da/ha` do cs.json (são horários de
   recebimento/totalização).
""")
    L.append("## Limitações\n")
    L.append("""- **Fechar depois das 17h não é prova de prorrogação.** Pela lei, quem está na fila às 17h vota; urnas com
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
""")
    out = a.saida_md or ("relatorio.md" if cargo == 1 else f"relatorio_{slug}.md")
    with open(out, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"ok: {out}, dados/secoes_{slug}.parquet ({os.path.getsize(f'dados/secoes_{slug}.parquet') / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
