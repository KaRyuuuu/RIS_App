# scripts/get_version.py
"""
Lit la version depuis ris_app/__init__.py
Retourne 0.0.0 si le fichier ou la variable n'existe pas
"""
from pathlib import Path
import re

try:
    p = Path("ris_app/__init__.py").read_text(encoding="utf-8")
    m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", p)
    print(m.group(1) if m else "0.0.0")
except Exception:
    print("0.0.0")
