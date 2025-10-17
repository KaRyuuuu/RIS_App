"""Système de mise à jour du coeur et des plugins."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests

from .. import __version__
from ..config import (
    CATALOG_CACHE_PATH,
    CATALOG_MAIN_URL,
    CATALOG_RELEASE_URL,
    PLUGINS_DIR,
    ROOT_DIR,
    TEMP_ARCHIVE_PREFIX,
    TEMP_UPDATE_DIR,
)
from ..utils import atomic_extract, get_logger, is_newer, sha256_file
from .plugin_manager import PluginManager

logger = get_logger(__name__)


@dataclass
class CatalogPlugin:
    """Représente un plugin décrit dans le catalogue distant."""

    slug: str
    version: str
    zip_url: str
    sha256: str


@dataclass
class Catalog:
    """Représente le catalogue complet (coeur + plugins)."""

    core_version: str
    core_zip_url: str
    core_sha256: str
    plugins: List[CatalogPlugin]

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Catalog":
        core = data.get("core", {})
        plugins_data = data.get("plugins", [])
        return cls(
            core_version=core.get("version", "0.0.0"),
            core_zip_url=core.get("zip_url", ""),
            core_sha256=core.get("sha256", ""),
            plugins=[CatalogPlugin(**plugin) for plugin in plugins_data],
        )


class UpdateError(RuntimeError):
    """Exception levée lorsqu'une mise à jour échoue."""


class Updater:
    """Vérifie et applique les mises à jour du coeur et des plugins."""

    def __init__(self, plugin_manager: PluginManager) -> None:
        self.plugin_manager = plugin_manager
        TEMP_UPDATE_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Téléchargement du catalogue
    # -------------------------
    def download_catalog(self) -> Catalog:
        """Télécharge le catalogue distant en utilisant l'URL de release puis le fallback."""

        urls = [CATALOG_RELEASE_URL, CATALOG_MAIN_URL]
        last_error: Optional[Exception] = None
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                CATALOG_CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
                return Catalog.from_dict(data)
            except Exception as exc:  # pragma: no cover - dépend du réseau
                logger.warning("Échec du téléchargement du catalogue depuis %s: %s", url, exc)
                last_error = exc

        raise UpdateError(f"Impossible de télécharger le catalogue: {last_error}")

    def load_local_catalog(self) -> Optional[Catalog]:
        """Charge le catalogue en cache si disponible."""

        if not CATALOG_CACHE_PATH.exists():
            return None
        try:
            data = json.loads(CATALOG_CACHE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.error("Catalogue local corrompu: %s", exc)
            return None
        return Catalog.from_dict(data)

    # -------------------------
    # Vérification des versions
    # -------------------------
    def check_updates(self, catalog: Catalog | None = None) -> Dict[str, str]:
        """Retourne un dictionnaire des éléments nécessitant une mise à jour."""

        catalog = catalog or self.load_local_catalog()
        if not catalog:
            raise UpdateError("Aucun catalogue disponible. Lancez 'ris update check' avec internet.")

        updates: Dict[str, str] = {}
        if is_newer(__version__, catalog.core_version):
            updates["core"] = catalog.core_version

        for plugin_meta in self.plugin_manager.list_plugins():
            for plugin_catalog in catalog.plugins:
                if plugin_catalog.slug == plugin_meta.slug and is_newer(
                    plugin_meta.version, plugin_catalog.version
                ):
                    updates[plugin_meta.slug] = plugin_catalog.version

        # Détection de nouveaux plugins qui n'existent pas localement.
        local_slugs = {meta.slug for meta in self.plugin_manager.list_plugins()}
        for plugin_catalog in catalog.plugins:
            if plugin_catalog.slug not in local_slugs:
                updates[plugin_catalog.slug] = f"{plugin_catalog.version} (nouveau)"

        return updates

    # -------------------------
    # Application des mises à jour
    # -------------------------
    def apply_updates(
        self,
        catalog: Catalog,
        *,
        core: bool = True,
        plugins: Iterable[str] | None = None,
        include_new_plugins: bool = True,
    ) -> List[Path]:
        """Télécharge et applique les mises à jour demandées.

        Returns
        -------
        List[Path]
            Liste des chemins mis à jour pour feedback utilisateur.
        """

        updated_paths: List[Path] = []
        if core and is_newer(__version__, catalog.core_version):
            logger.info("Téléchargement de la mise à jour du coeur %s", catalog.core_version)
            core_archive = self._download_file(catalog.core_zip_url)
            self._verify_checksum(core_archive, catalog.core_sha256)
            target = ROOT_DIR
            atomic_extract(core_archive, target)
            updated_paths.append(target)

        plugin_slugs = set(plugins or [])
        available = {item.slug: item for item in catalog.plugins}
        targets: List[str]
        if plugin_slugs:
            targets = list(plugin_slugs)
        else:
            targets = [meta.slug for meta in self.plugin_manager.list_plugins()]
            if include_new_plugins:
                targets.extend(slug for slug in available if slug not in targets)

        for slug in targets:
            catalog_plugin = available.get(slug)
            if not catalog_plugin:
                logger.debug("Aucune mise à jour disponible pour %s", slug)
                continue

            local_metadata = self.plugin_manager.get_metadata(slug)
            if local_metadata and not is_newer(local_metadata.version, catalog_plugin.version):
                logger.debug("Le plugin %s est à jour", slug)
                continue

            logger.info("Téléchargement de la mise à jour du plugin %s (%s)", slug, catalog_plugin.version)
            archive_path = self._download_file(catalog_plugin.zip_url)
            self._verify_checksum(archive_path, catalog_plugin.sha256)
            target_dir = PLUGINS_DIR / slug
            atomic_extract(archive_path, target_dir)
            updated_paths.append(target_dir)

        return updated_paths

    # -------------------------
    # Utilitaires internes
    # -------------------------
    def _download_file(self, url: str) -> Path:
        """Télécharge un fichier dans le dossier temporaire."""

        if not url:
            raise UpdateError("URL de téléchargement manquante dans le catalogue")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        suffix = Path(url).name
        handle, path_str = tempfile.mkstemp(prefix=TEMP_ARCHIVE_PREFIX, suffix=suffix)
        path = Path(path_str)
        with open(handle, "wb") as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
        return path

    def _verify_checksum(self, file_path: Path, expected_sha256: str) -> None:
        """Vérifie l'intégrité d'une archive téléchargée."""

        if not expected_sha256:
            logger.warning("Aucune empreinte fournie pour %s", file_path)
            return
        actual = sha256_file(file_path)
        if actual != expected_sha256:
            raise UpdateError(
                f"Empreinte invalide pour {file_path.name}: attendu {expected_sha256}, obtenu {actual}"
            )
