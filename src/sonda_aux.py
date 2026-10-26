"""Sonda temporária: imprime o aux.json de seções sem BU utilizável (ZZ)."""
import asyncio, json, sys
sys.path.insert(0, "src")
import tse

SECS = [("29173", "0001", "0494"), ("29254", "0001", "0001"), ("29629", "0001", "3014"), ("29750", "0001", "1703")]


async def main():
    cli = tse.Cliente(4)
    for mu, zo, se in SECS:
        d = tse.url_secao(3221, "zz", mu, zo, se)
        j = await cli.json(f"{d}/p003221-zz-m{mu}-z{zo}-s{se}-aux.json")
        print(mu, zo, se, json.dumps(j, ensure_ascii=False)[:1500])
        for h in j.get("hashes", []):
            for a in h.get("arq", []):
                try:
                    b = await cli.get(f"{d}/{h['hash']}/{a['nm']}")
                    print("   ", a, len(b), b[:60])
                except Exception as e:
                    print("   ", a, "ERRO", str(e)[-60:])
    await cli.fechar()

asyncio.run(main())
