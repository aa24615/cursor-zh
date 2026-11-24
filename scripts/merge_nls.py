#!/usr/bin/env python3
"""Merge translated NLS chunks into the zh-hans language pack."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "build" / "nls-manifest.json"
ZH_DIR = ROOT / "build" / "nls-zh"
PACK = ROOT / "i18n" / "vscode-language-pack-zh-hans" / "translations" / "main.i18n.json"

PLACEHOLDER = re.compile(r"\{[0-9]+\}")
KEYBINDING = re.compile(r"<keybinding:[^>]+>")
ICON = re.compile(r"\$\([A-Za-z0-9_-]+\)")


def counts(pattern: re.Pattern[str], text: str) -> dict[str, int]:
    found: dict[str, int] = {}
    for match in pattern.finditer(text):
        token = match.group(0)
        found[token] = found.get(token, 0) + 1
    return found


def load_translations() -> dict[str, str]:
    translations: dict[str, str] = {}
    for path in sorted(ZH_DIR.glob("chunk-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path} is not a JSON object")
        overlap = set(translations) & set(data)
        if overlap:
            raise SystemExit(f"{path} repeats ids: {sorted(overlap)[:5]}")
        for key, value in data.items():
            if not isinstance(value, str):
                raise SystemExit(f"{path} value for {key} is not a string")
            translations[key] = value
    return translations


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    translations = load_translations()
    missing = [item["id"] for item in manifest if item["id"] not in translations]
    if missing:
        raise SystemExit(f"missing {len(missing)} translations, first: {missing[:8]}")

    problems: list[str] = []
    for item in manifest:
        source = item["en"]
        target = translations[item["id"]]
        for pattern, label in (
            (PLACEHOLDER, "placeholder"),
            (KEYBINDING, "keybinding"),
            (ICON, "icon"),
        ):
            if counts(pattern, source) != counts(pattern, target):
                problems.append(f"{item['id']} {label}: {source!r} -> {target!r}")
        if source.count("&&") != target.count("&&"):
            problems.append(f"{item['id']} mnemonic: {source!r} -> {target!r}")
    if problems:
        report = ROOT / "build" / "nls-merge-problems.txt"
        report.write_text("\n".join(problems), encoding="utf-8")
        raise SystemExit(f"{len(problems)} placeholder mismatches, see {report}")

    pack = json.loads(PACK.read_text(encoding="utf-8"))
    contents = pack["contents"]
    added = 0
    replaced = 0
    for item in manifest:
        module = contents.setdefault(item["mod"], {})
        translated = translations[item["id"]]
        if item["key"] in module:
            if module[item["key"]] != translated:
                module[item["key"]] = translated
                replaced += 1
        else:
            module[item["key"]] = translated
            added += 1

    PACK.write_text(json.dumps(pack, ensure_ascii=False, indent="\t") + "\n", encoding="utf-8")
    print(f"merged added={added} replaced={replaced} total={len(manifest)}")


if __name__ == "__main__":
    sys.exit(main())
