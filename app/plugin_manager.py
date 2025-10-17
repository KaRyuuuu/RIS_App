"""Plugin discovery and management utilities."""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Type

import customtkinter as ctk

from .plugin_base import Plugin


class PluginManager:
    """Load and manage plugins from a given package."""

    def __init__(self, package: ModuleType, master: "ctk.CTkFrame") -> None:
        self.package = package
        self.master = master
        self._plugins: Dict[str, Plugin] = {}

    def discover(self) -> List[Type[Plugin]]:
        """Discover plugin classes in the package."""
        discovered: List[Type[Plugin]] = []
        package_path = Path(self.package.__file__).parent

        for module_info in pkgutil.iter_modules([str(package_path)]):
            module = importlib.import_module(f"{self.package.__name__}.{module_info.name}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and issubclass(attribute, Plugin) and attribute is not Plugin:
                    discovered.append(attribute)
        return discovered

    def load_plugins(self) -> None:
        """Instantiate and load all discovered plugins."""
        for plugin_cls in self.discover():
            plugin = plugin_cls()
            plugin.load(self.master)
            self._plugins[plugin.name] = plugin

    def unload_plugins(self) -> None:
        """Unload all currently loaded plugins."""
        for plugin in self._plugins.values():
            plugin.unload()
        self._plugins.clear()

    @property
    def plugin_names(self) -> List[str]:
        """Return the list of loaded plugin names."""
        return list(self._plugins.keys())
