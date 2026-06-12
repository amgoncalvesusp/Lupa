"""Save and load reproducible Lupa analysis project files."""

import json
from pathlib import Path
from typing import Dict

PROJECT_VERSION = 1


def save_project(path: str | Path, data: Dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"versao": PROJECT_VERSION, **data}
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_project(path: str | Path) -> Dict:
    source = Path(path)
    raw = json.loads(source.read_text(encoding="utf-8"))
    if raw.get("versao") != PROJECT_VERSION:
        raise ValueError(f"Versão de projeto não suportada: {raw.get('versao')}")

    files = [str(p) for p in raw.get("arquivos", [])]
    present = [p for p in files if Path(p).exists()]
    missing = [p for p in files if not Path(p).exists()]
    return {
        "versao": PROJECT_VERSION,
        "termos_raw": str(raw.get("termos_raw", "")),
        "flags": dict(raw.get("flags", {})),
        "arquivos": present,
        "ausentes": missing,
    }
