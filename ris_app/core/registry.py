"""Gestion du registre de plugins activés/désactivés."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from ..config import REGISTRY_PATH
from ..utils.log import get_logger

logger = get_logger(__name__)


class PluginRegistry:
    """Persistant l'état d'activation des plugins dans ``registry.json``."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or REGISTRY_PATH
        self._data: Dict[str, bool] = {}
        self.load()

    def load(self) -> None:
        """Charge le registre depuis le disque, en créant un fichier par défaut au besoin."""

        if not self.path.exists():
            logger.debug("Création d'un registre vide à %s", self.path)
            self._data = {}
            self.save()
            return

        try:
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Impossible de lire le registre des plugins: %s", exc)
            self._data = {}

    def save(self) -> None:
        """Enregistre le registre sur disque."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def is_enabled(self, slug: str, default: bool = True) -> bool:
        """Retourne l'état d'activation d'un plugin."""

        return self._data.get(slug, default)

    def set_enabled(self, slug: str, enabled: bool) -> None:
        """Met à jour l'état d'un plugin et persiste la valeur."""

        self._data[slug] = enabled
        self.save()

    def all(self) -> Dict[str, bool]:
        """Retourne une copie du registre complet."""

        return dict(self._data)
