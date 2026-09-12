"""Prepare GitHub Pages without recompressing any image, video, drawing or font.

Usage: python scripts/build_github_pages.py --base-path /portfolio/
Use --base-path / for a domain-root deployment. Python 3.10+; no dependencies.
The canonical dist folder is read only. Generated files go to ignored _site/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dist"
OUTPUT = ROOT / "_site"
REPORT = ROOT / ".build-reports" / "github-pages.json"


def normalize_base(value: str) -> str:
    if not value or value == "/":
        return "/"
    parts = value.strip("/").split("/")
    if any(part in ("", ".", "..") or not re.fullmatch(r"[A-Za-z0-9._-]+", part) for part in parts):
        raise ValueError("Base path must contain only simple URL path segments, such as /portfolio/.")
    return "/" + "/".join(parts) + "/"


def default_base() -> str:
    repository = os.environ.get("GITHUB_REPOSITORY", "nairabym-alt/portfolio")
    owner, _, name = repository.partition("/")
    return "/" if name.lower() == (owner + ".github.io").lower() else "/" + name + "/"


def mount_url(value: str, base: str) -> str:
    return base + value[1:] if value.startswith("/") and not value.startswith("//") else value


def map_content(value, base: str):
    if isinstance(value, dict):
        return {key: map_content(item, base) for key, item in value.items()}
    if isinstance(value, list):
        return [map_content(item, base) for item in value]
    if isinstance(value, str) and value.startswith("/media/"):
        return mount_url(value, base)
    return value


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError("The application changed; update the Pages adapter for: " + old)
    return text.replace(old, new, 1)


def adapt_app(text: str, base: str) -> str:
    text = replace_once(text, "(async function () {", "(async function () {\n  const BASE_PATH = " + json.dumps(base) + ";\n  const isSitePath = path => BASE_PATH === '/' || path === BASE_PATH.slice(0, -1) || path.startsWith(BASE_PATH);\n  const routePath = path => !isSitePath(path) ? '/__not_found__/' : (BASE_PATH === '/' ? path : (path.slice(BASE_PATH.length - 1) || '/'));")
    text = replace_once(text, "fetch('/content.json')", "fetch(BASE_PATH + 'content.json')")
    text = replace_once(text, "const href = p => `/${p.category}/${p.id}/`;", "const href = p => `${BASE_PATH}${p.category}/${p.id}/`;")
    text = text.replace('href="/', 'href="${BASE_PATH}')
    text = replace_once(text, "const parts=location.pathname.split('/').filter(Boolean);", "const parts=routePath(location.pathname).split('/').filter(Boolean);")
    text = replace_once(text, "if(url.origin!==location.origin||", "if(url.origin!==location.origin||!isSitePath(url.pathname)||")
    return text


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from content_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from content_strings(item)
    elif isinstance(value, str):
        yield value


def validate_references(base: str, data: dict) -> int:
    references = {value for value in content_strings(data) if value.startswith("/")}
    for path in OUTPUT.rglob("*.html"):
        references.update(re.findall(r'''(?:href|src)=["'](/(?!/)[^"']*)["']''', path.read_text("utf-8")))
    for path in OUTPUT.rglob("*.css"):
        references.update(re.findall(r'''url\(["']?(/(?!/)[^\s)"']+)["']?\)''', path.read_text("utf-8")))
    references.add(base + "content.json")
    references.update(base + category["id"] + "/" for category in data["categories"])
    references.update(base + project["category"] + "/" + project["id"] + "/" for project in data["projects"])
    references.update(base + route for route in ("", "about/", "contact/", "cv/"))
    failures = []
    for reference in sorted(references):
        url_path = unquote(urlsplit(reference).path)
        if not url_path.startswith(base):
            failures.append(reference + " (outside configured base)")
            continue
        target = (OUTPUT / url_path[len(base):]).resolve()
        if not target.is_relative_to(OUTPUT.resolve()):
            failures.append(reference + " (escapes output)")
        elif not (target.is_file() or (target.is_dir() and (target / "index.html").is_file())):
            failures.append(reference + " (missing)")
    if failures:
        raise RuntimeError("Broken local references:\n" + "\n".join(failures))
    return len(references)


def build(base: str) -> dict:
    base = normalize_base(base)
    if not (SOURCE / "content.json").is_file():
        raise RuntimeError("Missing canonical dist/content.json.")
    if SOURCE.is_symlink() or OUTPUT.is_symlink() or OUTPUT.resolve().parent != ROOT.resolve():
        raise RuntimeError("Source and output must be regular project directories.")
    paths = sorted(path for path in SOURCE.rglob("*") if path.is_file())
    if any(path.is_symlink() or not path.resolve().is_relative_to(SOURCE.resolve()) for path in paths):
        raise RuntimeError("Source contains linked or external files.")
    expected = {path.relative_to(SOURCE).as_posix() for path in paths} | {".nojekyll"}
    OUTPUT.mkdir(exist_ok=True)
    # Remove only stale files in the verified generated directory, never dist.
    for path in OUTPUT.rglob("*"):
        if path.is_symlink() or not path.resolve().is_relative_to(OUTPUT.resolve()):
            raise RuntimeError("Unexpected linked output path.")
        if path.is_file() and path.relative_to(OUTPUT).as_posix() not in expected:
            path.unlink()
    changed = []
    protected = []
    data = map_content(json.loads((SOURCE / "content.json").read_text("utf-8")), base)
    for source in paths:
        relative = source.relative_to(SOURCE)
        relative_name = relative.as_posix()
        destination = OUTPUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative_name == "content.json":
            destination.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")
        elif relative_name == "app.js":
            destination.write_text(adapt_app(source.read_text("utf-8"), base), "utf-8")
        elif source.suffix == ".html" and relative.parts[0] != "media":
            text = re.sub(r'''((?:href|src)=["'])(/(?!/)[^"']*)(["'])''', lambda match: match[1] + mount_url(match[2], base) + match[3], source.read_text("utf-8"))
            destination.write_text(text, "utf-8")
        elif relative_name in ("styles.css", "fonts/fonts.css"):
            text = re.sub(r'''(url\(["']?)(/(?!/)[^\s)"']+)(["']?\))''', lambda match: match[1] + mount_url(match[2], base) + match[3], source.read_text("utf-8"))
            destination.write_text(text, "utf-8")
        else:
            shutil.copy2(source, destination)
            source_hash, output_hash = sha256(source), sha256(destination)
            if source_hash != output_hash:
                raise RuntimeError("Copied asset differs from original: " + relative_name)
            protected.append({"path": relative_name, "bytes": source.stat().st_size, "sha256": source_hash})
            continue
        changed.append(relative_name)
    (OUTPUT / ".nojekyll").write_bytes(b"")
    references = validate_references(base, data)
    report = {"status": "PASS", "base_path": base, "source": "dist", "output": "_site", "source_files": len(paths), "source_bytes": sum(path.stat().st_size for path in paths), "output_bytes": sum(path.stat().st_size for path in OUTPUT.rglob("*") if path.is_file()), "local_references_checked": references, "unchanged_files_sha256_verified": len(protected), "media_files_sha256_verified": sum(item["path"].startswith("media/") for item in protected), "rewritten_text_files": changed, "unchanged_files": protected}
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in ("unchanged_files", "rewritten_text_files")}, indent=2))
    print("No media encoding or compression was performed. Integrity report: .build-reports/github-pages.json")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-path", default=default_base(), help="Public URL mount, e.g. /portfolio/ or /.")
    args = parser.parse_args()
    build(args.base_path)
