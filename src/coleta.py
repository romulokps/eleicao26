"""Coleta por UF: para cada seção baixa aux.json + BU (em memória), extrai campos e descarta o bruto.

Uso: python src/coleta.py --uf rr [--cargo 1] [--saida out] [--checkpoint checkpoint] [--limite N]

Saídas (em --saida):
  secoes_<cargo>_<uf>.parquet  uma linha por seção (zstd, tipos enxutos)
  meta_<cargo>_<uf>.json       contagens, fuso inferido, totais oficiais da UF, nomes de municípios
Checkpoint (em --checkpoint): <cargo>_<uf>.jsonl com as seções já processadas (só campos extraídos).
"""
import argparse
import asyncio
import json
import os
import sys
import time
from collections import Counter, defaultdict

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(__file__))
import bu as B  # noqa: E402
import tse  # noqa: E402

# flag_problema (bitmask)
F_SEM_AUX = 1          # aux.json inexistente/erro: seção sem arquivos publicados
F_SEM_BU = 2           # aux sem BU ou download do BU falhou
F_ERRO_DECODE = 4      # BU não decodificou
F_SEM_HORA = 8         # BU sem dataHoraEncerramento (ex.: votação manual / SA)
F_URNA_NAO_ORD = 16    # tipoUrna != 1 (urna de contingência/substituta)
F_TIPO_ARQ = 32        # tipoArquivo != 1 (BU de apuração / sistema de apuração / votação manual)
F_MULTI_BU = 64        # aux.json com mais de um conjunto de arquivos (reenvio / urna substituída)
F_SEM_CARGO = 128      # BU sem a eleição/cargo pedido
F_HORA_ESTRANHA = 256  # encerramento fora do dia da eleição ou antes das 16h (Brasília)
F_OUTROS_VOTOS = 512   # votos nominais em número fora dos 2 candidatos ou votos de legenda
F_FUSO_PADRAO = 1024   # fuso do município não pôde ser inferido; usado o padrão da UF

FLAGS = {F_SEM_AUX: "sem aux.json", F_SEM_BU: "sem BU", F_ERRO_DECODE: "erro ao decodificar BU",
         F_SEM_HORA: "sem horário de encerramento", F_URNA_NAO_ORD: "urna não ordinária (contingência)",
         F_TIPO_ARQ: "BU não é de votação em urna (SA/manual)", F_MULTI_BU: "mais de um BU publicado",
         F_SEM_CARGO: "BU sem o cargo", F_HORA_ESTRANHA: "horário de encerramento atípico",
         F_OUTROS_VOTOS: "votos fora dos 2 candidatos", F_FUSO_PADRAO: "fuso não inferido (padrão UF)"}
RETENTAR = F_SEM_AUX | F_SEM_BU  # falhas de download: não contam como processadas no checkpoint

# deslocamento (horas) a somar à hora local para obter Brasília (UTC-3), padrão por UF (sem horário de verão)
FUSO_UF = {"ac": 2, "am": 1, "ro": 1, "rr": 1, "mt": 1, "ms": 1}
ABERTURA_BRASILIA_H = 8  # urnas abrem às 8h de Brasília em todo o país (no exterior: 8h locais)


async def processar_secao(cli, pleito, eleicao, cargo, uf, mun, zona, secao):
    row = {"mun": mun, "zona": zona, "secao": secao, "flag": 0}
    d = tse.url_secao(pleito, uf, mun, zona, secao)
    try:
        aux = await cli.json(f"{d}/p{pleito:06d}-{uf}-m{mun}-z{zona}-s{secao}-aux.json")
    except Exception as e:  # noqa: BLE001
        row["flag"] |= F_SEM_AUX
        row["erro"] = str(e)[:200]
        return row
    hashes = aux.get("hashes", [])
    if len(hashes) > 1:
        row["flag"] |= F_MULTI_BU
    row["st"] = aux.get("st")
    # usa o conjunto mais recente que tenha BU
    alvo = None
    for h in hashes:
        for a in h.get("arq", []):
            if a.get("tp") == "bu":
                alvo = (h["hash"], a["nm"])
    if not alvo:
        row["flag"] |= F_SEM_BU
        return row
    try:
        raw = await cli.get(f"{d}/{alvo[0]}/{alvo[1]}")
    except Exception as e:  # noqa: BLE001
        row["flag"] |= F_SEM_BU
        row["erro"] = str(e)[:200]
        return row
    try:
        b = B.decode(raw)
    except Exception as e:  # noqa: BLE001
        row["flag"] |= F_ERRO_DECODE
        row["erro"] = repr(e)[:200]
        return row
    finally:
        del raw  # bruto descartado: nada vai para o disco
    if b.tipo_urna != 1:
        row["flag"] |= F_URNA_NAO_ORD
    if b.tipo_arquivo != 1:
        row["flag"] |= F_TIPO_ARQ
    row["tipo_urna"], row["tipo_arquivo"] = b.tipo_urna, b.tipo_arquivo
    row["abertura"], row["encerramento"], row["emissao"] = b.abertura, b.encerramento, b.emissao
    if not b.encerramento:
        row["flag"] |= F_SEM_HORA
    ele = b.eleicoes.get(eleicao)
    c = ele and ele["cargos"].get(cargo)
    if not c:
        row["flag"] |= F_SEM_CARGO
        if ele:
            row["aptos"] = ele["aptos"]
        return row
    row["aptos"] = ele["aptos"]
    row["comp"] = c["comp"]
    row["votos"] = [[t, n, q] for (t, n), q in c["votos"].items()]
    return row


def hora_local_min(s, data_ref):
    """'AAAAMMDDTHHMMSS' local -> minutos desde 00:00 do dia da eleição (pode passar de 1440)."""
    from datetime import date
    d, m, _ = B.hm_to_min(s)
    dias = (date(int(d[:4]), int(d[4:6]), int(d[6:8])) - data_ref).days
    return dias * 1440 + m


def inferir_fuso(rows, uf, data_ref):
    """Fuso por município: moda de (8h - hora local de abertura) nas seções que abriram até :30.

    Urnas abrem às 8h de Brasília no país todo; a hora local de abertura revela o fuso do relógio da urna.
    No exterior (ZZ) a abertura é às 8h locais, então o horário fica relativo ao horário local da votação.
    """
    votos = defaultdict(Counter)
    for r in rows:
        a = r.get("abertura")
        if a:
            m = hora_local_min(a, data_ref)
            if m % 60 <= 30:
                votos[r["mun"]][ABERTURA_BRASILIA_H - m // 60] += 1
    padrao = FUSO_UF.get(uf, 0)
    fuso = {}
    for mun, c in votos.items():
        h, n = c.most_common(1)[0]
        fuso[mun] = {"h": h, "n": n, "total": sum(c.values()), "padrao_uf": padrao}
    return fuso, padrao


def montar_tabela(uf, rows, fuso, padrao, cand_nums, data_ref):
    cols = {k: [] for k in ("uf", "mun", "zona", "secao", "hora_fechamento", "aptos", "comparecimento",
                            "votos_cand1", "votos_cand2", "brancos", "nulos", "flag_problema")}
    for r in sorted(rows, key=lambda r: (r["mun"], r["zona"], r["secao"])):
        flag = r["flag"]
        hora = None
        if r.get("encerramento"):
            f = fuso.get(r["mun"])
            off = f["h"] if f else padrao
            if not f:
                flag |= F_FUSO_PADRAO
            hora = hora_local_min(r["encerramento"], data_ref) + off * 60
            if hora < 16 * 60 or hora >= 1440:
                flag |= F_HORA_ESTRANHA
        v1 = v2 = bra = nul = 0
        for t, n, q in r.get("votos", []):
            if t == 1 and n == cand_nums[0]:
                v1 += q
            elif t == 1 and n == cand_nums[1]:
                v2 += q
            elif t == 2:
                bra += q
            elif t == 3:
                nul += q
            else:
                flag |= F_OUTROS_VOTOS
        tem_votos = "comp" in r
        cols["uf"].append(uf.upper())
        cols["mun"].append(int(r["mun"]))
        cols["zona"].append(int(r["zona"]))
        cols["secao"].append(int(r["secao"]))
        cols["hora_fechamento"].append(hora)
        cols["aptos"].append(r.get("aptos"))
        cols["comparecimento"].append(r.get("comp"))
        cols["votos_cand1"].append(v1 if tem_votos else None)
        cols["votos_cand2"].append(v2 if tem_votos else None)
        cols["brancos"].append(bra if tem_votos else None)
        cols["nulos"].append(nul if tem_votos else None)
        cols["flag_problema"].append(flag)
    schema = pa.schema([("uf", pa.dictionary(pa.int8(), pa.string())), ("mun", pa.int32()),
                        ("zona", pa.int16()), ("secao", pa.int16()), ("hora_fechamento", pa.int16()),
                        ("aptos", pa.int32()), ("comparecimento", pa.int32()), ("votos_cand1", pa.int32()),
                        ("votos_cand2", pa.int32()), ("brancos", pa.int32()), ("nulos", pa.int32()),
                        ("flag_problema", pa.int16())])
    arrays = [pa.array(cols["uf"]).dictionary_encode().cast(schema.field("uf").type)]
    arrays += [pa.array(cols[n], type=schema.field(n).type) for n in schema.names[1:]]
    return pa.Table.from_arrays(arrays, schema=schema)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uf", required=True)
    ap.add_argument("--cargo", type=int, default=1)
    ap.add_argument("--data", default="25/10/2026")
    ap.add_argument("--saida", default="out")
    ap.add_argument("--checkpoint", default="checkpoint")
    ap.add_argument("--concorrencia", type=int, default=15)
    ap.add_argument("--limite", type=int, default=0, help="processa só N seções (teste)")
    ap.add_argument("--tempo-max", type=float, default=0, help="minutos; para antes e deixa o resto p/ retomada")
    a = ap.parse_args()
    uf, cargo = a.uf.lower(), a.cargo
    from datetime import date
    dd, mm, aa = a.data.split("/")
    data_ref = date(int(aa), int(mm), int(dd))
    os.makedirs(a.saida, exist_ok=True)
    os.makedirs(a.checkpoint, exist_ok=True)
    t0 = time.time()
    cli = tse.Cliente(concorrencia=a.concorrencia)
    pleito, eleicao, nome, cargo_nome = await tse.descobrir_eleicao(cli, cargo, a.data)
    print(f"[{uf}] pleito {pleito} eleição {eleicao} ({nome}) cargo {cargo}", flush=True)

    # resultado oficial da UF (validação + números dos candidatos)
    oficial = None
    try:
        oficial = tse.resumo_oficial(await cli.json(tse.url_oficial(eleicao, uf, cargo)))
    except Exception as e:  # noqa: BLE001
        print(f"[{uf}] aviso: resultado oficial indisponível: {e}", flush=True)
    if oficial is None or len(oficial["cands"]) < 2:
        br = tse.resumo_oficial(await cli.json(tse.url_oficial(eleicao, "br", cargo)))
        cands = br["cands"]
    else:
        cands = oficial["cands"]
    cand_nums = sorted(cands)[:2]
    print(f"[{uf}] candidatos: {[(n, cands[n]['nm']) for n in cand_nums]}", flush=True)

    cs = await cli.json(tse.url_cs(pleito, uf))
    secoes, agregadas, nomes = [], [], {}
    for ab in cs["abr"]:
        for m in ab["mu"]:
            nomes[int(m["cd"])] = m["nm"]
            for z in m["zon"]:
                for s in z["sec"]:
                    if "nsp" in s:  # seção agregada: votos estão no BU da seção principal (nsp)
                        agregadas.append((m["cd"], z["cd"], s["ns"], s["nsp"]))
                    else:
                        secoes.append((m["cd"], z["cd"], s["ns"]))
    if a.limite:
        secoes = secoes[:: max(1, len(secoes) // a.limite)][: a.limite]
    print(f"[{uf}] {len(secoes)} seções ({len(agregadas)} agregadas fora da lista)", flush=True)

    ck_path = os.path.join(a.checkpoint, f"{cargo}_{uf}.jsonl")
    feitos = {}
    if os.path.exists(ck_path):
        with open(ck_path) as f:
            for ln in f:
                try:
                    r = json.loads(ln)
                except json.JSONDecodeError:
                    continue  # última linha truncada
                if not r["flag"] & RETENTAR:
                    feitos[(r["mun"], r["zona"], r["secao"])] = r
    pend = [s for s in secoes if s not in feitos]
    print(f"[{uf}] checkpoint: {len(feitos)} prontas, {len(pend)} a processar", flush=True)

    ck = open(ck_path, "a")
    novos = {}
    n_ok = 0
    fila = asyncio.Queue()
    for s in pend:
        fila.put_nowait(s)

    async def worker():
        nonlocal n_ok
        while True:
            if a.tempo_max and time.time() - t0 > a.tempo_max * 60:
                return
            try:
                s = fila.get_nowait()
            except asyncio.QueueEmpty:
                return
            r = await processar_secao(cli, pleito, eleicao, cargo, uf, *s)
            novos[s] = r
            ck.write(json.dumps(r, separators=(",", ":")) + "\n")
            n_ok += 1
            if n_ok % 500 == 0:
                ck.flush()
                el = time.time() - t0
                print(f"[{uf}] {n_ok}/{len(pend)}  {n_ok / el:.1f} seç/s  {cli.bytes / 1e6:.1f} MB", flush=True)

    await asyncio.gather(*(worker() for _ in range(a.concorrencia)))
    ck.close()
    await cli.fechar()
    if not fila.empty():
        print(f"[{uf}] tempo-max atingido: {fila.qsize()} seções pendentes ficam para a retomada", flush=True)
        sys.exit(3)

    rows = list(feitos.values()) + list(novos.values())
    fuso, padrao = inferir_fuso(rows, uf, data_ref)
    tab = montar_tabela(uf, rows, fuso, padrao, cand_nums, data_ref)
    pq.write_table(tab, os.path.join(a.saida, f"secoes_{cargo}_{uf}.parquet"), compression="zstd")

    flags = Counter()
    for f in tab.column("flag_problema").to_pylist():
        for bit in FLAGS:
            if f & bit:
                flags[bit] += 1
    erros = Counter(r.get("erro", "")[:80] for r in rows if r.get("erro"))
    tipos = Counter((r.get("tipo_urna"), r.get("tipo_arquivo")) for r in rows)
    divergentes = {m: f for m, f in fuso.items() if f["h"] != padrao and uf != "zz"}
    meta = {
        "uf": uf, "cargo": cargo, "cargo_nome": cargo_nome, "pleito": pleito, "eleicao": eleicao, "eleicao_nome": nome,
        "candidatos": [[n, cands[n]["nm"]] for n in cand_nums],
        "n_secoes": len(secoes), "n_agregadas": len(agregadas),
        "flags": {FLAGS[k]: v for k, v in sorted(flags.items())},
        "erros_exemplo": dict(erros.most_common(10)),
        "tipos_urna_arquivo": {f"{k[0]}/{k[1]}": v for k, v in tipos.items()},
        "fuso_padrao_uf_h": padrao,
        "fuso_municipios_divergentes": {str(k): v for k, v in divergentes.items()},
        "fuso_resumo": dict(Counter(f["h"] for f in fuso.values())),
        "municipios": {str(k): v for k, v in nomes.items()},
        "oficial": {k: v for k, v in (oficial or {}).items() if k != "cands"} | (
            {"cands": {str(k): v for k, v in oficial["cands"].items()}} if oficial else {}),
        "bytes_baixados": cli.bytes, "requisicoes": cli.reqs, "segundos": round(time.time() - t0, 1),
    }
    with open(os.path.join(a.saida, f"meta_{cargo}_{uf}.json"), "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)

    # validação contra o oficial da UF
    s = {c: sum(x or 0 for x in tab.column(c).to_pylist())
         for c in ("aptos", "comparecimento", "votos_cand1", "votos_cand2", "brancos", "nulos")}
    print(f"[{uf}] soma BUs: {s}", flush=True)
    if oficial:
        print(f"[{uf}] oficial: cand1={oficial['cands'].get(cand_nums[0], {}).get('vap')} "
              f"cand2={oficial['cands'].get(cand_nums[1], {}).get('vap')} brancos={oficial['brancos']} "
              f"nulos={oficial['nulos']} comparecimento={oficial['comparecimento']} "
              f"eleitorado={oficial['eleitorado']}", flush=True)
    print(f"[{uf}] flags: {meta['flags']}  fuso: {meta['fuso_resumo']} divergentes: {len(divergentes)}", flush=True)
    print(f"[{uf}] {cli.reqs} reqs, {cli.bytes / 1e6:.1f} MB em {meta['segundos']}s", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
