"""Fonctions d'entrée/sortie dédiées aux mises à jour et à la gestion des plugins."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable


def sha256_file(path: Path) -> str:
    """Calcule l'empreinte SHA-256 d'un fichier."""

    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def zip_dir(source_dir: Path, destination_zip: Path, *, exclude: Iterable[Path] | None = None) -> None:
    """Crée une archive ZIP à partir d'un dossier.

    Parameters
    ----------
    source_dir:
        Dossier à archiver.
    destination_zip:
        Chemin de l'archive à produire.
    exclude:
        Collection de chemins à exclure de l'archive.
    """

    exclude_set = {path.resolve() for path in (exclude or [])}
    with zipfile.ZipFile(destination_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for item in source_dir.rglob("*"):
            if any(item.is_relative_to(excluded) for excluded in exclude_set):
                continue
            archive.write(item, item.relative_to(source_dir))


def atomic_extract(zip_path: Path, target_dir: Path) -> None:
    """Extrait une archive dans un dossier en mode *swap* pour limiter les risques.

    L'extraction se fait dans un dossier temporaire qui remplace ensuite le dossier cible.
    Cela évite de laisser l'application dans un état partiellement mis à jour en cas d'erreur.
    """

    temp_dir = Path(tempfile.mkdtemp(prefix="ris_app_extract_"))
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(temp_dir)

        # Si le dossier cible existe déjà, nous le supprimons proprement.
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(str(temp_dir), str(target_dir))
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
