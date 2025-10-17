"""Configuration centrale de l'application.

Ce module regroupe les chemins d'accès importants ainsi que les URL utilisées pour les mises
à jour. Les constantes sont définies à l'aide de :class:`pathlib.Path` afin de garantir la
portabilité sur Windows, Linux et macOS.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

# Répertoire racine du projet (deux niveaux au-dessus de ce fichier).
ROOT_DIR: Final[Path] = Path(__file__).resolve().parent

# Dossiers internes.
DATA_DIR: Final[Path] = ROOT_DIR / "data"
PLUGINS_DIR: Final[Path] = ROOT_DIR / "plugins"
CACHE_DIR: Final[Path] = DATA_DIR

# Fichiers de données persistants.
CATALOG_CACHE_PATH: Final[Path] = DATA_DIR / "catalog.json"
REGISTRY_PATH: Final[Path] = DATA_DIR / "registry.json"

# URL du catalogue distant publié sur GitHub. Nous pointons d'abord vers la dernière release,
# puis nous fournissons un repli (fallback) sur la branche ``main`` si nécessaire.
CATALOG_RELEASE_URL: Final[str] = (
    "https://github.com/KaRyuuuuuu/RIS_app/releases/latest/download/catalog.json"
)
CATALOG_MAIN_URL: Final[str] = (
    "https://raw.githubusercontent.com/KaRyuuuuuu/RIS_app/main/ris_app/data/catalog.json"
)

# Dossier temporaire utilisé lors du téléchargement de mises à jour.
TEMP_UPDATE_DIR: Final[Path] = Path.home() / ".ris_app" / "updates"

# Nom du fichier dans lequel les archives téléchargées seront stockées.
TEMP_ARCHIVE_PREFIX: Final[str] = "ris_app_update_"

# Identifiant du logger principal.
LOGGER_NAME: Final[str] = "ris_app"
