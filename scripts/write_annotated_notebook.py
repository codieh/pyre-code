#!/usr/bin/env python3
"""
Write an annotated notebook from structured data.
Usage:
  python3 write_annotated_notebook.py <task_id> <variant> <solution_code> <summary_text> [--header <header_text>]

variant: "reference" or "interview"
solution_code: the annotated solution code (from stdin or file)
summary_text: the core summary markdown (from stdin or file)
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOLUTIONS_DIR = ROOT / "solutions"
TASKS_DIR = ROOT / "torch_judge" / "tasks"


def find_nb_number(task_id: str) -> str:
    """Find the number prefix of the existing solution notebook."""
    for p in sorted(SOLUTIONS_DIR.glob("*_solution.ipynb")):
        tid = re.sub(r"^\d+_", "", p.stem).replace("_solution", "")
        if tid == task_id:
            return p.name.split("_")[0]
    return "99"


def load_task(task_id: str) -> dict:
    ns = {}
    exec((TASKS_DIR / f"{task_id}.py").read_text(), ns)
    return ns["TASK"]


def build_header(task: dict, variant: str) -> str:
    tag = "面试版" if variant == "interview" else "参考版"
    title = task.get("title", task_id)
    difficulty = task.get("difficulty", "")
    desc_zh = task.get("description_zh", "")
    hint_zh = task.get("hint_zh", "")
    func_name = task.get("function_name", "")

    lines = [
        f"# 🔴 Solution: {title}（{tag}）",
        "",
        "## 📋 题目描述",
        "",
    ]
    if difficulty:
        lines += [f"**难度：** {difficulty}", ""]
    if desc_zh:
        lines += [desc_zh, ""]
    if hint_zh:
        lines += [f"**提示：** {hint_zh}", ""]
    return "\n".join(lines)


def make_notebook(header_md: str, solution_code: str, demo_code: str, judge_code: str, summary_md: str) -> dict:
    """Create a full notebook structure."""
    def code_cell(src):
        lines = src.split("\n")
        for i in range(len(lines) - 1):
            if not lines[i].endswith("\n"):
                lines[i] += "\n"
        return {
            "cell_type": "code",
            "execution_count": None,
            "id": None,
            "metadata": {},
            "outputs": [],
            "source": lines
        }

    def md_cell(src):
        lines = src.split("\n")
        for i in range(len(lines) - 1):
            if not lines[i].endswith("\n"):
                lines[i] += "\n"
        return {
            "cell_type": "markdown",
            "id": None,
            "metadata": {},
            "source": lines
        }

    cells = [
        md_cell(header_md),
        code_cell("import torch\nimport math"),
        code_cell(solution_code),
    ]
    if demo_code.strip():
        cells.append(code_cell(demo_code))
    if judge_code.strip():
        cells.append(code_cell(judge_code))
    if summary_md.strip():
        cells.append(md_cell(summary_md))

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11.0"}
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 write_annotated_notebook.py <task_id> <variant> <solution_file> <summary_file> [demo_file] [judge_file]")
        sys.exit(1)

    task_id = sys.argv[1]
    variant = sys.argv[2]  # "reference" or "interview"
    solution_file = Path(sys.argv[3])
    summary_file = Path(sys.argv[4])
    demo_file = Path(sys.argv[5]) if len(sys.argv) > 5 else None
    judge_file = Path(sys.argv[6]) if len(sys.argv) > 6 else None

    task = load_task(task_id)
    header = build_header(task, variant)
    solution_code = solution_file.read_text()
    summary_md = summary_file.read_text()
    demo_code = demo_file.read_text() if demo_file else ""
    judge_code = judge_file.read_text() if judge_file else ""

    nb = make_notebook(header, solution_code, demo_code, judge_code, summary_md)

    num = find_nb_number(task_id)
    suffix = "_interview" if variant == "interview" else "_solution"
    out_path = SOLUTIONS_DIR / f"{num}_{task_id}{suffix}.ipynb"

    out_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1))
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
