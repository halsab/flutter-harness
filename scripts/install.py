#!/usr/bin/env python3
"""Install/sync one managed Harness revision. Never overwrite app source."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

SOURCE = Path(__file__).resolve().parents[1]
START = "<!-- flutter-harness:start -->"
END = "<!-- flutter-harness:end -->"
BINS = ("harness.py","check.sh","check-runner.py","check-product.py","init-product.py","maestro.sh",
        "session-usage.py","task-plan.py","validate-opencode.py","web-preview.py")
IGNORES = ("/.flutter-harness/work/", "/.flutter-harness/previews/", "/.playwright/")
# Known retired managed paths, never arbitrary project files.
RETIRED = (".opencode/skills/flutter-harness/SKILL.md",
           ".flutter-harness/bin/verify-e2e.py", ".flutter-harness/bin/verify-pr.sh",
           ".flutter-harness/templates/product/PRODUCT.md",
           ".flutter-harness/templates/product/product.json",
           ".flutter-harness/HARNESS-REVISION.md")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(root, name):
    require(not Path(name).is_absolute() and ".." not in Path(name).parts, f"Unsafe managed path: {name}")
    path = root / name
    require(not any(p.is_symlink() for p in (path, *path.parents) if p != root and root in p.parents),
            f"Symlink in managed path: {name}")
    return path


def build(profile, base):
    result = {}
    for name in BINS:
        result[".flutter-harness/bin/" + name] = (SOURCE / "scripts" / name).read_bytes()
    for path in (SOURCE / "plugins/delivery-guard").glob("*"):
        if path.is_file():
            result[".opencode/plugins/delivery-guard/" + path.name] = path.read_bytes()
    template = SOURCE / "templates/product"
    result[".flutter-harness/PRODUCT.md"] = (template / "PRODUCT.md").read_bytes()
    for path in template.rglob("*"):
        if path.is_file() and path.name not in ("PRODUCT.md", "product.json"):
            result[".flutter-harness/templates/product/" + path.relative_to(template).as_posix()] = path.read_bytes()
    result[".github/workflows/flutter.yml"] = (SOURCE / "templates/project-ci.yml").read_text().replace("__HARNESS_BASE__", json.dumps(base)).encode()
    result["opencode.jsonc"] = (SOURCE / ("templates/opencode-" + profile + ".jsonc")).read_bytes()
    return result


def install(root, profile, base, adopt=False):
    require((root / "pubspec.yaml").is_file(), "Expected Flutter project")
    require(root != SOURCE, "Cannot install into Harness source")
    require(profile in ("mobile", "mobile-web"), "Invalid profile")
    require(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._/-]*", base), "Invalid base")
    subprocess.run(["git", "check-ref-format", "--branch", base], check=True,
                   stdout=subprocess.DEVNULL)
    require(not git(SOURCE,"status","--porcelain","--","scripts","plugins","templates"),
            "Commit Harness source changes before installing a revision")
    revision = git(SOURCE, "rev-parse", "HEAD")
    manifest_path = safe(root, ".flutter-harness/managed.json")
    config_path = safe(root, ".flutter-harness/config.json")
    agents_path = safe(root, "AGENTS.md")
    product_path = safe(root, ".flutter-harness/product.json")
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    require(not previous or previous.get("schema") == 2, "Unsupported managed manifest")
    old = previous.get("files", {})
    require(isinstance(old, dict) and all(name in (".flutter-harness/config.json", ".flutter-harness/PRODUCT.md", "opencode.jsonc", ".github/workflows/flutter.yml") or name.startswith((".flutter-harness/bin/", ".flutter-harness/templates/product/", ".opencode/plugins/delivery-guard/")) for name in old), "Invalid managed manifest paths")
    require(not adopt or not previous, "--adopt is for the one-time pre-schema-2 migration")
    if adopt:
        require(not git(root, "status", "--porcelain"), "Adoption requires a clean Git checkout")
    new = build(profile, base)
    new[".flutter-harness/config.json"] = (json.dumps({
        "schema": 2, "profile": profile, "integration_branch": base,
        "revision": revision}, indent=2) + "\n").encode()
    block = (SOURCE / "templates/PROJECT-AGENTS.md").read_text().strip()
    agents = agents_path.read_text() if agents_path.exists() else ""
    require(agents.count(START) == agents.count(END) and agents.count(START) <= 1,
            "Ambiguous managed AGENTS block")
    match = re.search(re.escape(START) + r"[\s\S]*?" + re.escape(END), agents)
    require(not previous or match, "Managed AGENTS block is missing")
    if match and previous:
        require(digest(match.group().encode()) == previous["agents_block"],
                "Local edits inside managed AGENTS block")
    elif match and not adopt:
        raise ValueError("Legacy managed AGENTS block; explicit clean --adopt required")
    new_agents = (agents[:match.start()] + block + agents[match.end():] if match
                  else agents.rstrip() + ("\n\n" if agents.strip() else "") + block + "\n")
    require(not (root / "opencode.json").exists(), "Existing opencode.json needs explicit manual reconciliation")
    safe(root, ".gitignore")
    # Preflight every write/removal before touching any managed file.
    for name in set(old) | set(new) | (set(RETIRED) if adopt else set()):
        path = safe(root, name)
        if not path.exists():
            if name in old:
                raise ValueError(f"Managed file removed locally: {name}")
            continue
        require(path.is_file(), f"Expected managed file: {name}")
        if name in old:
            require(digest(path.read_bytes()) == old[name], f"Local managed edits: {name}")
        elif name not in new or path.read_bytes() != new[name]:
            require(adopt, f"Existing unmanaged file: {name}; use clean --adopt only for known Harness installation")
            git(root, "ls-files", "--error-unmatch", "--", name)
    if adopt:
        require(config_path.exists() and
                json.loads(config_path.read_text()).get("source") == "https://github.com/halsab/flutter-harness",
                "Not a recognized pre-schema-2 Harness installation")
    for name, data in new.items():
        path = safe(root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
    for name in (set(old) - set(new)) | (set(RETIRED) if adopt else set()):
        safe(root, name).unlink(missing_ok=True)
    if not product_path.exists():
        product_path.write_bytes((SOURCE / "templates/product/product.json").read_bytes())
    agents_path.write_text(new_agents, encoding="utf-8")
    ignore = safe(root, ".gitignore")
    lines = ignore.read_text().splitlines() if ignore.exists() else []
    for entry in IGNORES:
        if entry not in lines:
            lines.append(entry)
    ignore.write_text("\n".join(lines) + "\n")
    manifest_path.write_text(json.dumps({
        "schema": 2, "revision": revision,
        "files": {name: digest(data) for name, data in sorted(new.items())},
        "agents_block": digest(block.encode())}, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "revision": revision, "profile": profile,
                      "integration_branch": base, "managed_files": len(new)}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("project", type=Path)
    p.add_argument("profile", choices=("mobile", "mobile-web"))
    p.add_argument("base")
    p.add_argument("--adopt", action="store_true")
    a = p.parse_args()
    try:
        install(a.project.resolve(), a.profile, a.base, a.adopt)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as e:
        print(f"BLOCKED: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
