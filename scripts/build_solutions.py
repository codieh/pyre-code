#!/usr/bin/env python3
"""Pre-process solution notebooks into a static JSON file for the frontend.

Supports two variants per problem:
  - reference: *_solution.ipynb  (marker: # ✅ SOLUTION)
  - interview: *_interview.ipynb (marker: # ✅ INTERVIEW)
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOLUTIONS_DIR = ROOT / "solutions"
OUTPUT = ROOT / "web" / "src" / "lib" / "solutions.json"

SKIP_PATTERNS = ("google.colab", "torch_judge", "get_ipython", "colab.research.google.com")
SOLUTION_MARKER = re.compile(r"#\s*✅\s*SOLUTION")
INTERVIEW_MARKER = re.compile(r"#\s*✅\s*INTERVIEW")


def strip_markers(src: str) -> str:
    """Remove # ✅ SOLUTION and # ✅ INTERVIEW marker lines, keep other comments."""
    lines = [
        l for l in src.splitlines()
        if not SOLUTION_MARKER.match(l.strip()) and not INTERVIEW_MARKER.match(l.strip())
    ]
    return "\n".join(lines).strip()


def strip_imports(src: str) -> str:
    lines = [l for l in src.splitlines() if not l.startswith("import ") and not l.startswith("from ")]
    return "\n".join(lines).strip()


def process_notebook(path: Path, marker: re.Pattern) -> list[dict]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    cells = []
    for c in nb.get("cells", []):
        src = "".join(c["source"])
        if not src.strip() or any(s in src for s in SKIP_PATTERNS):
            continue
        if c["cell_type"] == "code":
            is_solution = bool(marker.search(src))
            stripped = strip_imports(strip_markers(src))
            if not stripped:
                continue
            role = "solution" if is_solution else "demo"
            cells.append({"type": "code", "source": stripped, "role": role})
        else:
            cells.append({"type": c["cell_type"], "source": src.strip(), "role": "explanation"})
    return cells


def extract_task_id(nb_path: Path) -> str:
    """Extract task_id from filename like '16_cross_entropy_solution.ipynb'."""
    return re.sub(r"^\d+_", "", nb_path.stem).replace("_solution", "").replace("_interview", "")


def main():
    result = {}

    # Process reference solutions (*_solution.ipynb)
    for nb_path in sorted(SOLUTIONS_DIR.glob("*_solution.ipynb")):
        task_id = extract_task_id(nb_path)
        cells = process_notebook(nb_path, SOLUTION_MARKER)
        if not cells:
            print(f"WARNING: no cells for {task_id} (reference)")
            continue
        result.setdefault(task_id, {})["reference"] = cells

    # Process interview solutions (*_interview.ipynb)
    for nb_path in sorted(SOLUTIONS_DIR.glob("*_interview.ipynb")):
        task_id = extract_task_id(nb_path)
        cells = process_notebook(nb_path, INTERVIEW_MARKER)
        if not cells:
            print(f"WARNING: no cells for {task_id} (interview)")
            continue
        result.setdefault(task_id, {})["interview"] = cells

    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    ref_count = sum(1 for v in result.values() if "reference" in v)
    int_count = sum(1 for v in result.values() if "interview" in v)
    print(f"Written {len(result)} solutions to {OUTPUT.relative_to(ROOT)} "
          f"({ref_count} reference, {int_count} interview)")


if __name__ == "__main__":
    main()
