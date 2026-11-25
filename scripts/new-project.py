#!/usr/bin/env python3
"""Create and verify a fresh standard Flutter project, never migrate an existing app."""
import argparse
from pathlib import Path
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def run(*args, cwd=None):
    subprocess.run(args, cwd=cwd, check=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", type=Path)
    p.add_argument("name")
    p.add_argument("org")
    p.add_argument("profile", choices=("mobile","mobile-web"))
    p.add_argument("base")
    a = p.parse_args()
    root = a.path.resolve()
    if (root.exists() and (not root.is_dir() or any(x.name != ".git" for x in root.iterdir()))) or not re.fullmatch(r"[a-z][a-z0-9_]*", a.name):
        p.error("Expected an empty directory or empty Git repository and snake_case project name")
    existing_git = (root/".git").exists()
    if existing_git:
        if not (root/".git").is_dir() or (root/".git").is_symlink():
            p.error("Expected a normal Git repository")
        try:
            branch = subprocess.check_output(["git","symbolic-ref","--short","HEAD"],cwd=root,text=True).strip()
            tracked = subprocess.check_output(["git","ls-files","-z"],cwd=root)
            status = subprocess.check_output(["git","status","--porcelain"],cwd=root)
        except subprocess.CalledProcessError:
            p.error("Invalid existing Git repository")
        if branch != a.base or tracked or status:
            p.error("Existing empty repository must be on the requested integration branch with no tracked files or pending changes")
    run("git","check-ref-format","--branch",a.base)
    platforms = "android,ios,web" if a.profile == "mobile-web" else "android,ios"
    run("flutter","create","--empty","--project-name",a.name,"--org",a.org,"--platforms",platforms,str(root))
    if not existing_git:
        if (root/".git").exists():
            run("git","symbolic-ref","HEAD","refs/heads/"+a.base,cwd=root)
        else:
            run("git","init","-b",a.base,str(root))
    run(sys.executable,str(HERE/"install.py"),str(root),a.profile,a.base)
    run(sys.executable,str(HERE/"init-product.py"),str(root))
    template = HERE.parent / "templates/product"
    # These files belong to the new project just created above.
    (root/"lib/main.dart").write_bytes((template/"lib/main.dart.template").read_bytes())
    test = root/"test"
    test.mkdir(exist_ok=True)
    (test/"material_test.dart").write_text((template/"smoke_test.dart.template").read_text().replace("package:harness_product_smoke/", f"package:{a.name}/"))
    run("flutter","pub","add","material_ui:^1.1.0",cwd=root)
    product = root/".flutter-harness/product.json"
    data = json.loads(product.read_text())
    data["status"] = "active"
    product.write_text(json.dumps(data,indent=2)+"\n")
    try:
        run(sys.executable,str(root/".flutter-harness/bin/harness.py"),"check",cwd=root)
    except subprocess.CalledProcessError:
        data["status"] = "pending"
        product.write_text(json.dumps(data,indent=2)+"\n")
        raise
    run("git","add","-A",cwd=root)
    run("git","commit","-m","chore: initialize Flutter product and Harness",cwd=root)
    print("PASS fresh product; configure Git origin before first task")
if __name__ == "__main__":
    main()
