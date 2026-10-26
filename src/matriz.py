"""Monta os parâmetros da execução (matrix de UFs) a partir dos inputs do workflow ou de execucao.json."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from tse import UFS  # noqa: E402

cfg = {"cargo": "1", "ufs": "todas", "limite": "0", "commit": "true"}
if os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch" and os.path.exists("execucao.json"):
    cfg.update({k: str(v).lower() for k, v in json.load(open("execucao.json")).items()})
for k in cfg:
    v = os.environ.get(f"IN_{k.upper()}")
    if v:
        cfg[k] = v.strip().lower()
ufs = UFS if cfg["ufs"] in ("todas", "all", "br", "") else [u.strip() for u in cfg["ufs"].replace(";", ",").split(",") if u.strip()]
bad = [u for u in ufs if u not in UFS]
if bad:
    raise SystemExit(f"UF inválida: {bad}")
print(f"ufs={json.dumps(ufs)}")
print(f"ufs_csv={','.join(ufs)}")
print(f"cargo={int(cfg['cargo'])}")
print(f"limite={int(cfg['limite'])}")
print(f"commit={'true' if cfg['commit'] in ('true', '1', 'sim', 'yes') else 'false'}")
