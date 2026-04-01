from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import streamlit


def _streamlit_static_root() -> Path:
    return Path(streamlit.__file__).resolve().parent / "static"


def _load_dependency_paths(static_root: Path) -> list[Path]:
    index_html = (static_root / "index.html").read_text(encoding="utf-8")
    main_match = re.search(r'src="./static/js/([^"]+)"', index_html)
    if not main_match:
        raise RuntimeError("Khong tim thay file JS chinh cua Streamlit trong index.html")

    main_js = static_root / "static" / "js" / main_match.group(1)
    script = main_js.read_text(encoding="utf-8")
    deps_match = re.search(r"m\.f\|\|\(m\.f=\[(.*?)\]\)", script, re.S)
    if not deps_match:
        raise RuntimeError("Khong phan tich duoc danh sach chunk cua Streamlit")

    dependencies = json.loads(f"[{deps_match.group(1)}]")
    resolved_paths = []
    for dependency in dependencies:
        filename = Path(dependency).name
        folder = "css" if dependency.endswith(".css") else "js"
        resolved_paths.append(static_root / "static" / folder / filename)
    return resolved_paths


def _missing_dependencies() -> list[Path]:
    static_root = _streamlit_static_root()
    missing = []
    for path in _load_dependency_paths(static_root):
        if not path.exists():
            missing.append(path)
    return missing


def _repair_streamlit_installation() -> None:
    version = streamlit.__version__
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "--force-reinstall",
            f"streamlit=={version}",
        ]
    )


def main() -> int:
    missing = _missing_dependencies()
    if not missing:
        print("Streamlit static assets OK")
        return 0

    print("Phat hien Streamlit static assets bi thieu:")
    for path in missing[:20]:
        print(f"- {path.name}")
    if len(missing) > 20:
        print(f"- ... va {len(missing) - 20} file khac")

    print("Dang cai dat lai Streamlit de sua bo static assets...")
    _repair_streamlit_installation()

    remaining = _missing_dependencies()
    if remaining:
        print("Van con file Streamlit bi thieu sau khi cai dat lai:")
        for path in remaining[:20]:
            print(f"- {path.name}")
        return 1

    print("Da sua xong Streamlit static assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
