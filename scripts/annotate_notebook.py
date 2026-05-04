#!/usr/bin/env python3
"""
Annotate a solution notebook with teaching-style Chinese comments.
Usage:
  python3 annotate_notebook.py <task_id> [--interview]

This script:
1. Reads the task definition from torch_judge/tasks/<task_id>.py
2. Reads the solution notebook
3. Adds problem description header, teaching comments, and summary
4. Writes back to the notebook
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOLUTIONS_DIR = ROOT / "solutions"
TASKS_DIR = ROOT / "torch_judge" / "tasks"


def find_notebook(task_id: str, interview: bool = False) -> Path | None:
    """Find the solution notebook for a given task_id."""
    pattern = f"*_{task_id}_solution.ipynb" if not interview else f"*_{task_id}_interview.ipynb"
    matches = list(SOLUTIONS_DIR.glob(pattern))
    if matches:
        return matches[0]
    # Try without number prefix
    if interview:
        return SOLUTIONS_DIR / f"{task_id}_interview.ipynb"
    return SOLUTIONS_DIR / f"{task_id}_solution.ipynb"


def load_task(task_id: str) -> dict | None:
    """Load task definition from torch_judge/tasks/<task_id>.py."""
    task_file = TASKS_DIR / f"{task_id}.py"
    if not task_file.exists():
        return None
    content = task_file.read_text(encoding="utf-8")
    # Extract TASK dict by evaluating it
    local_ns = {}
    exec(content, local_ns)
    return local_ns.get("TASK")


def get_solution_source(nb: dict) -> str:
    """Extract the solution code from the notebook."""
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])
            if "✅ SOLUTION" in src or "✅ INTERVIEW" in src:
                # Remove marker lines and import lines
                lines = []
                for line in src.split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("# ✅"):
                        continue
                    if stripped.startswith("import ") or stripped.startswith("from "):
                        continue
                    lines.append(line)
                return "\n".join(lines).strip()
    return ""


def build_problem_header(task: dict, interview: bool = False) -> list[str]:
    """Build the problem description markdown lines."""
    lines = []
    title = task.get("title", "")
    difficulty = task.get("difficulty", "")
    desc_zh = task.get("description_zh", "")
    hint_zh = task.get("hint_zh", "")

    variant_tag = "面试版" if interview else "参考版"
    lines.append(f"# 🔴 Solution: {title}（{variant_tag}）")
    lines.append("")
    lines.append("## 📋 题目描述")
    lines.append("")

    if difficulty:
        lines.append(f"**难度：** {difficulty}")
        lines.append("")

    if desc_zh:
        # Parse description for signature, params, returns, constraints
        lines.append(desc_zh)
        lines.append("")

    if hint_zh:
        lines.append(f"**提示：** {hint_zh}")
        lines.append("")

    return lines


def create_notebook(cells: list[dict]) -> dict:
    """Create a notebook structure."""
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }


def make_code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": None,
        "metadata": {},
        "outputs": [],
        "source": source.split("\n")
    }


def make_markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": None,
        "metadata": {},
        "source": source.split("\n")
    }


# Ensure each line ends with \n except the last
def fix_newlines(cell: dict) -> dict:
    for i in range(len(cell["source"]) - 1):
        if not cell["source"][i].endswith("\n"):
            cell["source"][i] += "\n"
    return cell


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 annotate_notebook.py <task_id> [--interview]")
        sys.exit(1)

    task_id = sys.argv[1]
    is_interview = "--interview" in sys.argv

    task = load_task(task_id)
    if not task:
        print(f"ERROR: Task '{task_id}' not found in {TASKS_DIR}")
        sys.exit(1)

    nb_path = find_notebook(task_id, interview=False)
    if not nb_path or not nb_path.exists():
        print(f"ERROR: Reference notebook not found for '{task_id}'")
        sys.exit(1)

    print(f"Processing: {task_id} (interview={is_interview})")
    print(f"  Reference notebook: {nb_path}")
    print(f"  Task title: {task.get('title', 'N/A')}")

    if is_interview:
        interview_path = find_notebook(task_id, interview=True)
        if interview_path and interview_path.exists():
            print(f"  Interview notebook already exists: {interview_path}")
        else:
            print(f"  Will create interview notebook: {interview_path}")

    print(f"  Solution preview: {get_solution_source(nb_path)[:100]}...")
    print("Ready for annotation.")


if __name__ == "__main__":
    main()
