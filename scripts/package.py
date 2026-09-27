from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
ARCHIVES = {
    "chatgpt": "tizzy-rblx-advisor-chatgpt.zip",
    "claude": "tizzy-rblx-advisor-claude.zip",
    "universal": "tizzy-rblx-advisor-universal.zip",
}


def read_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path} is missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path} has unterminated YAML frontmatter") from exc
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def validate_source() -> str:
    manifest_paths = [
        ROOT / "plugin.json",
        ROOT / ".codex-plugin" / "plugin.json",
        ROOT / ".claude-plugin" / "plugin.json",
    ]
    versions = {
        json.loads(path.read_text(encoding="utf-8-sig"))["version"]
        for path in manifest_paths
    }
    if len(versions) != 1:
        raise ValueError(f"Plugin versions do not match: {sorted(versions)}")

    skill_dir = ROOT / "skills" / "tizzy-advisor"
    meta = read_frontmatter(skill_dir / "SKILL.md")
    if meta.get("name") != skill_dir.name:
        raise ValueError(
            f"Skill name {meta.get('name')!r} must match folder {skill_dir.name!r}"
        )
    if len(meta.get("name", "")) > 64:
        raise ValueError("Skill name exceeds Claude's 64-character limit")
    if len(meta.get("description", "")) > 200:
        raise ValueError("Skill description exceeds Claude's 200-character limit")
    return next(iter(versions))


def zip_bytes(entries: list[tuple[str, bytes]]) -> bytes:
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:
        for arcname, data in sorted(entries, key=lambda item: item[0]):
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return buffer.getvalue()


TEXT_SUFFIXES = {".json", ".md", ".py", ".txt", ".yml", ".yaml", ".toml"}
TEXT_NAMES = {".gitignore", ".gitattributes"}


def canonical_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES:
        text = data.decode("utf-8-sig")
        return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return data


def file_entry(path: Path, arcname: str | None = None) -> tuple[str, bytes]:
    return (arcname or path.relative_to(ROOT).as_posix(), canonical_bytes(path))


def skill_entries(prefix: str = "skills/tizzy-advisor", lower_skill_name: bool = False):
    skill_root = ROOT / "skills" / "tizzy-advisor"
    entries: list[tuple[str, bytes]] = []
    for path in sorted(p for p in skill_root.rglob("*") if p.is_file()):
        rel = path.relative_to(skill_root).as_posix()
        if lower_skill_name and rel == "SKILL.md":
            rel = "skill.md"
        entries.append(file_entry(path, f"{prefix}/{rel}"))
    return entries


def build_archives(output: Path) -> None:
    validate_source()
    output.mkdir(parents=True, exist_ok=True)

    chatgpt_entries = [
        file_entry(ROOT / "plugin.json"),
        file_entry(ROOT / ".codex-plugin" / "plugin.json"),
        *skill_entries(),
    ]
    (output / ARCHIVES["chatgpt"]).write_bytes(zip_bytes(chatgpt_entries))

    claude_entries = skill_entries(prefix="tizzy-advisor", lower_skill_name=True)
    (output / ARCHIVES["claude"]).write_bytes(zip_bytes(claude_entries))

    excluded_roots = {".git", "dist", "__pycache__"}
    universal_entries: list[tuple[str, bytes]] = []
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file()):
        rel = path.relative_to(ROOT)
        if any(part in excluded_roots for part in rel.parts):
            continue
        if path.suffix == ".pyc":
            continue
        universal_entries.append(file_entry(path))
    (output / ARCHIVES["universal"]).write_bytes(zip_bytes(universal_entries))

    checksum_lines = []
    for name in sorted(ARCHIVES.values()):
        digest = hashlib.sha256((output / name).read_bytes()).hexdigest()
        checksum_lines.append(f"{digest}  {name}")
    (output / "SHA256SUMS.txt").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8", newline="\n"
    )


def check_committed_dist() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        expected = Path(tmp)
        build_archives(expected)
        names = [*ARCHIVES.values(), "SHA256SUMS.txt"]
        mismatches = []
        for name in names:
            committed = DIST / name
            generated = expected / name
            if not committed.is_file() or committed.read_bytes() != generated.read_bytes():
                mismatches.append(name)
        if mismatches:
            print("Distribution files are stale:", ", ".join(mismatches), file=sys.stderr)
            print("Run: python scripts/package.py", file=sys.stderr)
            return 1
    print("Committed distribution matches a fresh deterministic build.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build portable Tizzy RBLX Advisor packages")
    parser.add_argument("--output", type=Path, help="Write packages to this directory")
    parser.add_argument("--check", action="store_true", help="Verify committed dist is current")
    args = parser.parse_args()

    if args.check:
        return check_committed_dist()

    output = args.output or DIST
    build_archives(output)
    print(f"Built release packages in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())