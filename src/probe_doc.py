"""Procura o pacote de documentação técnica (spec ASN.1 do BU) no site do TSE."""
import re, io, zipfile, sys, httpx
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
pages = [
 "https://www.tse.jus.br/eleicoes/eleicoes-2026/documentacao-tecnica-do-software-da-urna-eletronica",
 "https://www.tse.jus.br/eleicoes/eleicoes-2024/documentacao-tecnica-do-software-da-urna-eletronica",
 "https://www.tse.jus.br/eleicoes/eleicoes-2022/documentacao-tecnica-do-software-da-urna-eletronica",
]
with httpx.Client(timeout=60, follow_redirects=True, headers=H) as c:
    for p in pages:
        try:
            r = c.get(p)
        except Exception as e:
            print(p, "ERR", e); continue
        print(p, r.status_code, len(r.content))
        links = set(re.findall(r'href="([^"]+)"', r.text))
        for l in sorted(links):
            if re.search(r"zip|asn|download|bu|arquivo", l, re.I) and "javascript" not in l:
                print("   ", l)
