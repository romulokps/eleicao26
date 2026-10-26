"""Acesso HTTP ao resultados.tse.jus.br: cliente assíncrono com retry/backoff e descoberta da eleição."""
import asyncio
import random

import httpx

BASE = "https://resultados.tse.jus.br/oficial"
UFS = ("ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to zz").split()


class NaoEncontrado(Exception):
    pass


class Cliente:
    def __init__(self, concorrencia=15, timeout=30.0, tentativas=6):
        self.sem = asyncio.Semaphore(concorrencia)
        self.tentativas = tentativas
        self.bytes = 0
        self.reqs = 0
        self.http = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=15.0),
            limits=httpx.Limits(max_connections=concorrencia, max_keepalive_connections=concorrencia),
            headers={"User-Agent": "eleicao26-analise (github.com/romulokps/eleicao26)"},
            follow_redirects=True,
        )

    async def get(self, url) -> bytes:
        """GET com retry exponencial (+jitter).

        O bucket S3 do TSE responde 403/404 tanto para arquivo inexistente quanto, sob carga, de forma
        transitória; por isso 403/404 também são re-tentados (até 3 vezes) antes de virar NaoEncontrado.
        """
        espera = 1.0
        nao_achou = 0
        for t in range(self.tentativas):
            try:
                async with self.sem:
                    r = await self.http.get(url)
                self.reqs += 1
                if r.status_code == 200:
                    self.bytes += len(r.content)
                    return r.content
                if r.status_code in (403, 404):
                    nao_achou += 1
                    if nao_achou >= 3:
                        raise NaoEncontrado(f"{url}: HTTP {r.status_code}")
                erro = f"HTTP {r.status_code}"
            except NaoEncontrado:
                raise
            except (httpx.TransportError, httpx.TimeoutException) as e:
                erro = repr(e)
            if t == self.tentativas - 1:
                raise RuntimeError(f"{url}: {erro}")
            await asyncio.sleep(espera + random.random())
            espera = min(espera * 2, 60)

    async def json(self, url):
        import json
        return json.loads(await self.get(url))

    async def fechar(self):
        await self.http.aclose()


async def descobrir_eleicao(cli: Cliente, cargo: int, data="25/10/2026", ano="ele2026"):
    """Acha (pleito, eleição) do turno na data dada que contém o cargo, via ele-c.json."""
    ele = await cli.json(f"{BASE}/comum/config/ele-c.json")
    for pl in ele["pl"]:
        if pl.get("c") != ano or pl.get("dt") != data:
            continue
        for e in pl["e"]:
            if e.get("tp") not in ("1", "8") or "Ordinária" not in e.get("nm", ""):
                continue
            cargos = {cp["cd"]: cp["ds"] for a in e.get("abr", []) for cp in a.get("cp", [])}
            if str(cargo) in cargos:
                return int(pl["cd"]), int(e["cd"]), e["nm"], cargos[str(cargo)]
    raise SystemExit(f"eleição não encontrada para cargo {cargo} em {data}")


def url_cs(pleito, uf, ano="ele2026"):
    return f"{BASE}/{ano}/arquivo-urna/{pleito}/config/{uf}/{uf}-p{pleito:06d}-cs.json"


def url_secao(pleito, uf, mun, zona, secao, ano="ele2026"):
    return f"{BASE}/{ano}/arquivo-urna/{pleito}/dados/{uf}/{mun}/{zona}/{secao}"


def url_oficial(eleicao, uf, cargo, ano="ele2026"):
    return f"{BASE}/{ano}/{eleicao}/dados/{uf}/{uf}-c{cargo:04d}-e{eleicao:06d}-u.json"


def resumo_oficial(j):
    """Extrai totais e votos por candidato do JSON de totalização (…-u.json)."""
    cands = {}

    def walk(o):
        if isinstance(o, dict):
            if "vap" in o and "n" in o and "nm" in o:
                cands[int(o["n"])] = {"nm": o.get("nmu") or o["nm"], "vap": int(o["vap"] or 0)}
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(j)

    def num(d, k):
        try:
            return int(str(d.get(k, "")).replace(".", ""))
        except ValueError:
            return None
    s, e, v = j.get("s", {}), j.get("e", {}), j.get("v", {})
    return {
        "cands": cands,
        "secoes_total": num(s, "ts"), "secoes_totalizadas": num(s, "st"),
        "eleitorado": num(e, "te"), "comparecimento": num(e, "c"), "abstencao": num(e, "a"),
        "brancos": num(v, "vb"), "nulos": num(v, "tvn"), "validos": num(v, "vvc"),
        "raw_s": s, "raw_e": e, "raw_v": v,
        "dt_totalizacao": f"{j.get('dt')} {j.get('ht')}",
    }
