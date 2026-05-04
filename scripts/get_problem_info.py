#!/usr/bin/env python3
"""Get all info needed to annotate a problem: task definition + current solution code."""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOLUTIONS_DIR = ROOT / "solutions"
TASKS_DIR = ROOT / "torch_judge" / "tasks"

def find_nb(task_id, interview=False):
    suffix = "_interview" if interview else "_solution"
    for p in sorted(SOLUTIONS_DIR.glob(f"*{suffix}.ipynb")):
        tid = re.sub(r"^\d+_", "", p.stem).replace(suffix, "")
        if tid == task_id:
            return p
    return None

def extract_solution(nb_path, marker="# ✅"):
    nb = json.loads(nb_path.read_text())
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])
            if marker in src:
                return src
    return ""

def main():
    task_id = sys.argv[1]
    task_file = TASKS_DIR / f"{task_id}.py"
    if not task_file.exists():
        print(f"ERROR: {task_file} not found"); sys.exit(1)
    
    ns = {}
    exec(task_file.read_text(), ns)
    task = ns["TASK"]
    
    ref_nb = find_nb(task_id, False)
    int_nb = find_nb(task_id, True)
    
    print(f"=== TASK: {task_id} ===")
    print(f"Title: {task.get('title','')}")
    print(f"Difficulty: {task.get('difficulty','')}")
    print(f"Description (zh):\n{task.get('description_zh','')}")
    print(f"\nHint (zh): {task.get('hint_zh','')}")
    print(f"\nFunction: {task.get('function_name','')}")
    
    if ref_nb:
        print(f"\n=== REFERENCE SOLUTION ({ref_nb.name}) ===")
        print(extract_solution(ref_nb, "# ✅ SOLUTION"))
    
    if int_nb:
        print(f"\n=== INTERVIEW SOLUTION ({int_nb.name}) ===")
        print(extract_solution(int_nb, "# ✅ INTERVIEW"))
    else:
        print(f"\n=== NO INTERVIEW VERSION YET ===")

if __name__ == "__main__":
    main()
