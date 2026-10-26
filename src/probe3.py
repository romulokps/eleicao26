"""Sonda 3: dump completo do EntidadeBoletimUrna (conteúdo do envelope) de 2 seções."""
import asyncio, sys, httpx
sys.path.insert(0, "src")
from probe2 import tlv_dump  # noqa

BASE = "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/dados"
SECS = [("rr", "03123", "0007", "0001"), ("rr", "03018", "0001", "0712")]


def inner(b):
    # envelope: SEQ { cab, fase, ident, tipo, OCTET STRING conteudo }
    i = b.rfind(b"\x04\x82")
    L = int.from_bytes(b[i+2:i+4], "big")
    return b[i+4:i+4+L]


async def main():
    async with httpx.AsyncClient(timeout=60) as c:
        for uf, mu, zo, se in SECS:
            d = f"{BASE}/{uf}/{mu}/{zo}/{se}"
            j = (await c.get(f"{d}/p003221-{uf}-m{mu}-z{zo}-s{se}-aux.json")).json()
            h = j["hashes"][0]
            nm = [a["nm"] for a in h["arq"] if a["tp"] == "bu"][0]
            b = (await c.get(f"{d}/{h['hash']}/{nm}")).content
            print(f"\n##### {uf} {mu} {zo} {se}")
            print("\n".join(tlv_dump(inner(b), out=[])))
            for a in h["arq"]:
                for ext in ["imgbu", "vota"]:
                    pass
            # tenta variações de nome do imgbu
            for nm2 in [nm.replace("-bu.dat", "-imgbu.dat"), nm.replace("-bu.dat", ".imgbu"),
                        nm.replace("-bu.dat", "-imgbu.txt")]:
                r = await c.get(f"{d}/{h['hash']}/{nm2}")
                print("try", nm2, r.status_code, len(r.content))


asyncio.run(main())
