"""Sonda 5: encontra a URL do resultado oficial (JSON de totalização) da eleição."""
import asyncio, httpx
B = "https://resultados.tse.jus.br/oficial"
E, P = "6258", "3221"
cands = []
for ele in ("ele2026",):
    for e in (E, P):
        for uf in ("br", "rr"):
            for sub in ("dados-simplificados", "dados"):
                for suf in ("r", "f", "v", "u", "t"):
                    for ep in (f"e{int(E):06d}", f"e{E}"):
                        cands.append(f"{B}/{ele}/{e}/{sub}/{uf}/{uf}-c0001-{ep}-{suf}.json")
    cands += [f"{B}/{ele}/{E}/config/mun-e{int(E):06d}-cm.json",
              f"{B}/{ele}/{E}/config/br/br-e{int(E):06d}-i.json",
              f"{B}/comum/config/ele-c.json"]


async def main():
    async with httpx.AsyncClient(timeout=30) as c:
        sem = asyncio.Semaphore(10)
        async def get(u):
            async with sem:
                r = await c.get(u)
                if r.status_code == 200 and "-c0001-" in u:
                    j = r.json()
                    print("JSON", u, {k: v for k, v in j.items() if not isinstance(v, (list, dict))})
                    for cc in j.get("cand", [])[:4]:
                        print("   cand", cc)
                    for k, v in j.items():
                        if isinstance(v, list) and k != "cand": print("   list", k, str(v)[:300])
                return u, r.status_code, ""
        res = await asyncio.gather(*(get(u) for u in cands))
        for u, s, t in res:
            if s == 200:
                print("OK", u)
        print("404s:", sum(1 for _, s, _ in res if s != 200))

asyncio.run(main())
