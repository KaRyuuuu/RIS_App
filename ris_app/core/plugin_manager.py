"""Gestionnaire de plugins."""

from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from ..config import PLUGINS_DIR
from ..utils.log import get_logger
from .plugin_base import IPlugin
from .registry import PluginRegistry

logger = get_logger(__name__)


@dataclass
class PluginMetadata:
    """Métadonnées minimales d'un plugin."""

    name: str
    slug: str
    version: str
    author: str
    description: str
    entry: str
    enabled: bool
    path: Path


class PluginLoadError(RuntimeError):
    """Erreur levée lorsqu'un plugin ne peut pas être chargé."""


class PluginManager:
    """Découvre, charge et gère les plugins installés."""

    def __init__(self, plugins_dir: Path | None = None, registry: Optional[PluginRegistry] = None) -> None:
        self.plugins_dir = plugins_dir or PLUGINS_DIR
        self.registry = registry or PluginRegistry()
        self.plugins: Dict[str, IPlugin] = {}
        self.metadata: Dict[str, PluginMetadata] = {}
        self.discover_plugins()

    def discover_plugins(self) -> None:
        """Parcourt le dossier ``plugins`` et charge les métadonnées disponibles."""

        self.plugins.clear()
        self.metadata.clear()
        if not self.plugins_dir.exists():
            logger.info("Aucun dossier de plugins trouvé à %s", self.plugins_dir)
            return

        for plugin_json in self.plugins_dir.glob("*/plugin.json"):
            try:
                data = json.loads(plugin_json.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                logger.error("Plugin %s invalide: %s", plugin_json.parent.name, exc)
                continue

            if not {"name", "slug", "version", "entry"}.issubset(data):
                logger.error("Plugin %s invalide: métadonnées manquantes", plugin_json.parent.name)
                continue

            metadata = PluginMetadata(
                name=data["name"],
                slug=data["slug"],
                version=data["version"],
                author=data.get("author", "Inconnu"),
                description=data.get("description", ""),
                entry=data["entry"],
                enabled=data.get("enabled", True),
                path=plugin_json.parent,
            )

            self.metadata[metadata.slug] = metadata

            if self.registry.is_enabled(metadata.slug, metadata.enabled):
                try:
                    self.load_plugin(metadata)
                except PluginLoadError as exc:
                    logger.error("Impossible de charger le plugin %s: %s", metadata.slug, exc)

    def load_plugin(self, metadata: PluginMetadata) -> None:
        """Charge dynamiquement un plugin à partir de ses métadonnées."""

        module_name, _, class_name = metadata.entry.partition(":")
        if not module_name or not class_name:
            raise PluginLoadError("Entrée invalide, attendu 'module:Classe'.")

        module_path = f"ris_app.plugins.{metadata.slug}.{module_name}"
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as exc:
            raise PluginLoadError(f"Module introuvable: {module_path}") from exc

        try:
            plugin_class = getattr(module, class_name)
        except AttributeError as exc:
            raise PluginLoadError(f"Classe {class_name} introuvable dans {module_path}") from exc

        plugin = plugin_class()
        if not isinstance(plugin, IPlugin):
            raise PluginLoadError("La classe doit hériter de IPlugin")

        plugin.activate()
        self.plugins[metadata.slug] = plugin

    def list_plugins(self) -> List[PluginMetadata]:
        """Retourne la liste des métadonnées connues."""

        return list(self.metadata.values())

    def enable(self, slug: str) -> bool:
        """Active un plugin et le charge si nécessaire."""

        metadata = self.metadata.get(slug)
        if not metadata:
            logger.error("Plugin %s inconnu", slug)
            return False

        self.registry.set_enabled(slug, True)
        if slug not in self.plugins:
            try:
                self.load_plugin(metadata)
            except PluginLoadError as exc:
                logger.error("Erreur lors du chargement du plugin %s: %s", slug, exc)
                return False
        return True

    def disable(self, slug: str) -> bool:
        """Désactive un plugin et appelle ``deactivate`` si disponible."""

        plugin = self.plugins.pop(slug, None)
        if not plugin:
            logger.warning("Plugin %s déjà désactivé ou inconnu", slug)
        else:
            plugin.deactivate()
        self.registry.set_enabled(slug, False)
        return True

    def run_command(self, slug: str, command: str, *args: str) -> bool:
        """Exécute une commande fournie par un plugin."""

        plugin = self.plugins.get(slug)
        if not plugin:
            logger.error("Plugin %s non chargé. Activez-le d'abord.", slug)
            return False

        commands = plugin.get_commands_dict()
        callback = commands.get(command)
        if not callback:
            logger.error("Commande %s inconnue pour le plugin %s", command, slug)
            return False

        callback(*args)
        return True

    def get_plugin(self, slug: str) -> Optional[IPlugin]:
        """Retourne une instance de plugin si elle est chargée."""

        return self.plugins.get(slug)

    def get_metadata(self, slug: str) -> Optional[PluginMetadata]:
        """Retourne les métadonnées d'un plugin."""

        return self.metadata.get(slug)
