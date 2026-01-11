#!/usr/bin/env python3
"""
Consolidate documentation for Project Aegis Forge.
- Merge SESSION_SUMMARY.md and AGENT_03_PROGRESS.md into PROJECT_STATUS.md
- Merge VACCINE_005_MODEL_VERSIONING.md details into ai_learnings_v2.md
- Consolidate backend/README.md and frontend/README.md into README_DOCS.md
- Update README_DOCS.md links
- Delete merged redundant files and empty docs/

Run:
  python scripts/consolidate_docs.py
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent

# Files
PROJECT_STATUS = ROOT / "PROJECT_STATUS.md"
SESSION_SUMMARY = ROOT / "SESSION_SUMMARY.md"
AGENT_03_PROGRESS = ROOT / "AGENT_03_PROGRESS.md"
ai_LEARNINGS_V2 = ROOT / "ai_learnings_v2.md"
VACCINE_005 = ROOT / "VACCINE_005_MODEL_VERSIONING.md"
README_DOCS = ROOT / "README_DOCS.md"
BACKEND_README = ROOT / "backend" / "README.md"
FRONTEND_README = ROOT / "frontend" / "README.md"
DOCS_DIR = ROOT / "docs"

FILES_TO_DELETE = [SESSION_SUMMARY, AGENT_03_PROGRESS, VACCINE_005, FRONTEND_README]

# Utility functions

def backup(file: Path):
    if file.exists():
        bak = file.with_suffix(file.suffix + ".bak")
        shutil.copyfile(file, bak)
        print(f"Backup created: {bak}")


def append_section(file: Path, title: str, content: str):
    if not file.exists():
        print(f"WARN: Target file not found, creating: {file}")
        file.touch()
    backup(file)
    with file.open("a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write(f"## {title}\n\n")
        f.write(content.strip() + "\n")
    print(f"Appended section '{title}' → {file}")


def read_text(file: Path) -> str:
    if not file.exists():
        print(f"WARN: Missing file: {file}")
        return ""
    return file.read_text(encoding="utf-8")


def update_readme_docs(backend_readme: str):
    content = read_text(README_DOCS)
    if not content:
        content = "# 📚 Índice de Documentación - Proyecto Aegis Forge\n\n"
    backup(README_DOCS)

    # Remove references to files that will be deleted
    lines = content.splitlines()
    filtered = []
    to_remove_tokens = [
        "SESSION_SUMMARY.md",
        "AGENT_03_PROGRESS.md",
        "VACCINE_005_MODEL_VERSIONING.md",
    ]
    for line in lines:
        if any(tok in line for tok in to_remove_tokens):
            continue
        filtered.append(line)

    # Append consolidated setup sections
    consolidated_sections = "\n\n## Backend Setup (Consolidado)\n" \
        "\nRequisitos:\n- Python 3.12+\n- GOOGLE_API_KEY en .env (raíz)\n" \
        "\nInstalación y ejecución:\n\n```bash\ncd backend\npip install -r requirements.txt\npython main.py\n```\n" \
        "\nNotas:\n- Modelos centralizados en backend/model_config.py (Vacuna #005)\n- CORS abierto en dev; restringir en prod (Vacuna #004)\n\n" \
        "\n## Frontend Setup (Consolidado)\n" \
        "\nInstalación y ejecución:\n\n```bash\ncd frontend\nnpm install\nnpm run dev\n```\n" \
        "\nNotas:\n- Usa NEXT_PUBLIC_API_URL para apuntar al backend\n- No usar URLs hardcoded (Vacuna #004)\n"

    new_content = "\n".join(filtered) + consolidated_sections
    README_DOCS.write_text(new_content, encoding="utf-8")
    print(f"Updated consolidated README: {README_DOCS}")


def try_delete(path: Path):
    if path.is_file() and path.exists():
        path.unlink()
        print(f"Deleted file: {path}")
    elif path.is_dir() and path.exists():
        try:
            path.rmdir()
            print(f"Deleted empty directory: {path}")
        except OSError:
            print(f"Directory not empty, skipping: {path}")


def main():
    # 1) Merge SESSION_SUMMARY.md into PROJECT_STATUS.md → "Última Sesión"
    session_text = read_text(SESSION_SUMMARY)
    if session_text:
        append_section(PROJECT_STATUS, "Última Sesión (fusionada)", session_text)

    # 2) Merge AGENT_03_PROGRESS.md into PROJECT_STATUS.md → "Agentes → Constructor"
    agent_text = read_text(AGENT_03_PROGRESS)
    if agent_text:
        append_section(PROJECT_STATUS, "Agentes → Constructor (fusión de progreso)", agent_text)

    # 3) Merge VACCINE_005_MODEL_VERSIONING.md into ai_learnings_v2.md → "Vacuna #005: Detalle y remediación"
    vaccine_text = read_text(VACCINE_005)
    if vaccine_text:
        append_section(ai_LEARNINGS_V2, "Vacuna #005: Detalle y remediación (consolidado)", vaccine_text)

    # 4) Consolidate backend/README.md + frontend/README.md into README_DOCS.md
    backend_readme = read_text(BACKEND_README)
    update_readme_docs(backend_readme)

    # 5) Delete redundant files
    for f in FILES_TO_DELETE:
        try_delete(f)

    # 6) Delete empty docs/ if empty
    if DOCS_DIR.exists() and not any(DOCS_DIR.iterdir()):
        try_delete(DOCS_DIR)

    print("\nConsolidation complete. Backups created alongside modified files.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
