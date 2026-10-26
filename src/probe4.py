"""Sonda 4: testa bu.decode em N seções, hash do aux e URL do resultado oficial."""
import asyncio, sys, json, hashlib, base64, httpx
sys.path.insert(0, "src")
import bu as B

BASE = "https://resultados.tse.jus.br/oficial"
ARQ = f"{BASE}/ele2026/arquivo-urna/3221"


async def main(uf, n):
    async with httpx.AsyncClient(timeout=60) as c:
        cs = (await c.get(f"{ARQ}/config/{uf}/{uf}-p003221-cs.json")).json()
        secs = [(m["cd"], z["cd"], s["ns"]) for a in cs["abr"] for m in a["mu"] for z in m["zon"]
                for s in z["sec"] if "nsp" not in s]
        step = max(1, len(secs) // n)
        for k, (mu, zo, se) in enumerate(secs[::step][:n]):
            d = f"{ARQ}/dados/{uf}/{mu}/{zo}/{se}"
            j = (await c.get(f"{d}/p003221-{uf}-m{mu}-z{zo}-s{se}-aux.json")).json()
            h = j["hashes"][-1]
            nm = [a["nm"] for a in h["arq"] if a["tp"] == "bu"][0]
            raw = (await c.get(f"{d}/{h['hash']}/{nm}")).content
            b = B.decode(raw)
            p = b.eleicoes.get(6258, {}).get("cargos", {}).get(1)
            print(mu, zo, se, len(raw), "urna", b.tipo_urna, "arq", b.tipo_arquivo, "ab", b.abertura,
                  "enc", b.encerramento, "aptos", b.eleicoes.get(6258, {}).get("aptos"),
                  "comp", p and p["comp"], "votos", p and sorted(p["votos"].items()),
                  "ele", list(b.eleicoes))
            if k == 0:
                hs = bytes.fromhex(h["hash"]).decode()
                print("hash aux decodificado:", hs)
                for nmh in ("sha256", "sha512", "sha3_256", "sha3_512"):
                    dg = hashlib.new(nmh, raw).digest()
                    print(nmh, base64.b64encode(dg).decode(), base64.urlsafe_b64encode(dg).decode())
        for u in [f"{BASE}/ele2026/6258/dados-simplificados/{uf}/{uf}-c0001-e006258-r.json",
                  f"{BASE}/ele2026/6258/dados-simplificados/br/br-c0001-e006258-r.json",
                  f"{BASE}/ele2026/6258/dados/{uf}/{uf}-c0001-e006258-v.json"]:
            r = await c.get(u)
            print("\nOFICIAL", u, r.status_code)
            if r.status_code == 200:
                print(r.text[:2500])


asyncio.run(main(sys.argv[1], int(sys.argv[2])))
