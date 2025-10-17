"""Definitions for the plugin interface used by the CustomTkinter app."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only used for type checking
    import customtkinter as ctk


class Plugin(ABC):
    """Abstract base class that all plugins must inherit from."""

    name: str = "Unnamed Plugin"

    @abstractmethod
    def load(self, master: "ctk.CTkFrame") -> None:
        """Load the plugin into the provided master frame."""

    @abstractmethod
    def unload(self) -> None:
        """Unload and cleanup any UI resources created by the plugin."""
