"""Sonda a estrutura real dos dados do TSE (roda no GitHub Actions).

Imprime: código da eleição, amostra do cs.json, aux.json de algumas seções,
tamanhos de .bu/.imgbu e o texto do .imgbu. Nada é gravado em disco além
do pacote de documentação técnica (spec ASN.1), quando encontrado.
"""
import asyncio, json, re, sys, io, zipfile, os
import httpx

BASE = "https://resultados.tse.jus.br/oficial"
UF = sys.argv[1] if len(sys.argv) > 1 else "rr"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20


def short(o, n=1500):
    s = json.dumps(o, ensure_ascii=False)
    return s[:n]


async def main():
    async with httpx.AsyncClient(timeout=60, follow_redirects=True,
                                 headers={"User-Agent": "Mozilla/5.0 eleicao26-probe"}) as c:
        r = await c.get(f"{BASE}/comum/config/ele-c.json")
        print("ele-c status", r.status_code, len(r.content))
        ele = r.json()
        print(short(ele, 4000))
        # procurar eleições de 2026
        txt = json.dumps(ele, ensure_ascii=False)
        print("\n--- pleitos/eleicoes ---")
        def walk(o, path=""):
            if isinstance(o, dict):
                if "cd" in o and ("dt" in o or "nm" in o or "t" in o or "tp" in o):
                    print(path, {k: v for k, v in o.items() if not isinstance(v, (list, dict))})
                for k, v in o.items():
                    walk(v, path + "/" + k)
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, f"{path}[{i}]")
        walk(ele)


if __name__ == "__main__":
    asyncio.run(main())
