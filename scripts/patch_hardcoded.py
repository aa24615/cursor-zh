#!/usr/bin/env python3
"""Replace hardcoded UI string literals in Cursor workbench bundles.

Only strings used as React/UI property values are rewritten. Backups are
stored next to the originals as <file>.cursor-zh.bak and can be restored.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROPS = (
    "children",
    "title",
    "placeholder",
    "aria-label",
    "ariaLabel",
    "label",
    "description",
    "tooltip",
    "heading",
    "subtitle",
    "emptyText",
    "confirmText",
    "cancelText",
    "buttonText",
    "helperText",
    "errorText",
)
PROP_RE = re.compile(
    r"(?P<prop>" + "|".join(PROPS) + r"):\"(?P<text>(?:[^\"\\]|\\.)*)\""
)
DEFAULT_APP = Path("/Applications/Cursor.app/Contents/Resources/app/out/vs/workbench")
BUNDLES = (
    "workbench.glass.main.js",
    "workbench.desktop.main.js",
    "workbench.anysphere-ui-automations.js",
    "workbench.xai-commerce-prepaid.js",
)


def js_string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def load_dict(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must be a JSON object of english -> chinese")
    return {str(key): str(value) for key, value in data.items() if key != value}


def patch_text(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        raw = match.group("text")
        try:
            decoded = json.loads('"' + raw + '"')
        except json.JSONDecodeError:
            return match.group(0)
        translated = mapping.get(decoded)
        if translated is None:
            return match.group(0)
        count += 1
        return f"{match.group('prop')}:{js_string(translated)}"

    return PROP_RE.sub(replace, text), count


def check_syntax(path: Path) -> None:
    subprocess.run(["node", "--check", str(path)], check=True)


def restore(directory: Path) -> None:
    restored = 0
    for name in BUNDLES:
        backup = directory / f"{name}.cursor-zh.bak"
        target = directory / name
        if backup.exists():
            shutil.copy2(backup, target)
            restored += 1
    print(f"restored {restored} bundles")


def install(directory: Path, mapping: dict[str, str]) -> None:
    total = 0
    for name in BUNDLES:
        target = directory / name
        if not target.exists():
            print(f"skip missing {target}")
            continue
        backup = directory / f"{name}.cursor-zh.bak"
        if not backup.exists():
            shutil.copy2(target, backup)
        original = backup.read_text(encoding="utf-8")
        patched, count = patch_text(original, mapping)
        if count == 0:
            print(f"{name}: no replacements")
            continue
        target.write_text(patched, encoding="utf-8")
        check_syntax(target)
        total += count
        print(f"{name}: {count} replacements")
    print(f"patched {total} UI strings")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dict", type=Path, required=False)
    parser.add_argument("--app", type=Path, default=DEFAULT_APP)
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    if args.restore:
        restore(args.app)
        return
    if args.dict is None:
        raise SystemExit("--dict is required unless --restore is set")
    install(args.app, load_dict(args.dict))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
