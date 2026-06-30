"""Save and load reproducible Lupa analysis project files."""

import json
from pathlib import Path
from typing import Dict

PROJECT_VERSION = 2


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
    version = raw.get("versao")
    if version not in {1, PROJECT_VERSION}:
        raise ValueError(f"Versão de projeto não suportada: {raw.get('versao')}")

    flags = dict(raw.get("flags", {}))
    if version == 1:
        flags = {**flags, "presidente": False}

    files = [str(p) for p in raw.get("arquivos", [])]
    present = [p for p in files if Path(p).exists()]
    missing = [p for p in files if not Path(p).exists()]
    return {
        "versao": PROJECT_VERSION,
        "termos_raw": str(raw.get("termos_raw", "")),
        "flags": flags,
        "arquivos": present,
        "ausentes": missing,
        "metadata_overrides": dict(raw.get("metadata_overrides", {})),
        "entity_aliases": dict(raw.get("entity_aliases", {})),
        "count_mode": str(raw.get("count_mode", "integral")),
        "online_metadata": bool(raw.get("online_metadata", False)),
        "coding_records": [dict(record) for record in raw.get("coding_records", []) if isinstance(record, dict)],
    }
