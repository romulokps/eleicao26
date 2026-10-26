"""Sonda 2: estrutura de cs.json / aux.json / .bu / .imgbu em N seções de uma UF."""
import asyncio, json, re, sys, io, zipfile
import httpx

BASE = "https://resultados.tse.jus.br/oficial"
PLEITO, UF, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
ARQ = f"{BASE}/ele2026/arquivo-urna/{PLEITO}"


def tlv_dump(b, depth=0, maxdepth=12, out=None, pos=0, end=None):
    """Dump genérico de DER/BER (sem spec), para mapear campos."""
    end = len(b) if end is None else end
    while pos < end:
        t0 = b[pos]; cls = t0 >> 6; cons = bool(t0 & 0x20); tag = t0 & 0x1F; pos += 1
        if tag == 0x1F:
            tag = 0
            while True:
                x = b[pos]; pos += 1; tag = (tag << 7) | (x & 0x7F)
                if not x & 0x80: break
        L = b[pos]; pos += 1
        if L & 0x80:
            n = L & 0x7F; L = int.from_bytes(b[pos:pos+n], "big"); pos += n
        v = b[pos:pos+L]
        pre = "  " * depth + f"[{'UACP'[cls]}{tag}{'*' if cons else ''}] len={L}"
        if cons and depth < maxdepth:
            out.append(pre)
            tlv_dump(b, depth+1, maxdepth, out, pos, pos+L)
        else:
            s = v[:40]
            txt = s.decode("latin1") if all(32 <= c < 127 for c in s) and s else s.hex()
            iv = int.from_bytes(v, "big", signed=True) if 0 < L <= 8 else None
            out.append(pre + f" {txt!r}" + (f" int={iv}" if iv is not None else ""))
        pos += L
    return out


async def main():
    async with httpx.AsyncClient(timeout=60, follow_redirects=True,
                                 headers={"User-Agent": "Mozilla/5.0 eleicao26"}) as c:
        url = f"{ARQ}/config/{UF}/{UF}-p{int(PLEITO):06d}-cs.json"
        r = await c.get(url); print("CS", url, r.status_code, len(r.content))
        cs = r.json()
        print(json.dumps(cs, ensure_ascii=False)[:1200])
        secs = []
        for a in cs["abr"]:
            for m in a["mu"]:
                for z in m["zon"]:
                    for s in z["sec"]:
                        secs.append((a["cd"].lower(), m["cd"], z["cd"], s["ns"], s))
        print("n secoes", len(secs), "exemplo", secs[:2])
        step = max(1, len(secs)//N)
        tot = {"bu": 0, "imgbu": 0}
        for i, (uf, mu, zo, se, raw) in enumerate(secs[::step][:N]):
            d = f"{ARQ}/dados/{uf}/{mu}/{zo}/{se}"
            aux = f"{d}/p{int(PLEITO):06d}-{uf}-m{mu}-z{zo}-s{se}-aux.json"
            r = await c.get(aux)
            print(f"\n=== {uf} {mu} {zo} {se} aux {r.status_code} {len(r.content)}B")
            if r.status_code != 200:
                print("RAW cs entry:", raw); continue
            j = r.json()
            if i < 2 or len(j.get("hashes", [])) != 1: print(json.dumps(j, ensure_ascii=False)[:900])
            for h in j.get("hashes", []):
                for a in h.get("arq", []):
                    nm, ext = a["nm"], a["tp"]
                    if ext not in ("bu", "imgbu"): continue
                    fu = f"{d}/{h['hash']}/{nm}"
                    rr = await c.get(fu); tot[ext] += len(rr.content)
                    print(f"  {nm} {rr.status_code} {len(rr.content)}B")
                    if i < 2 and ext == "imgbu":
                        print(rr.content.decode("latin1")[:6000])
                    if i < 2 and ext == "bu":
                        print("\n".join(tlv_dump(rr.content, out=[])[:400]))
        print("\nTOTAL bytes", tot)


if __name__ == "__main__":
    asyncio.run(main())
