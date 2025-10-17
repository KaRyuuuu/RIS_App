"""Entry point for the CustomTkinter application with plugin and auto-update support."""
from __future__ import annotations

import threading
from pathlib import Path

import customtkinter as ctk

from .auto_updater import AutoUpdater
from .plugin_manager import PluginManager
from .version import __version__
import app.plugins as plugins_package


class Application(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CTk App avec plugin et mise à jour")
        self.geometry("520x400")
        ctk.set_default_color_theme("blue")

        self._build_ui()

        manifest_path = Path(__file__).resolve().parent.parent / "resources" / "update_manifest.json"
        self.auto_updater = AutoUpdater(manifest_path.as_uri(), Path(__file__).resolve().parent.parent)
        self.status_label.configure(textvariable=self.auto_updater.status_var)

        self.plugin_manager = PluginManager(plugins_package, self.plugin_frame)
        self.plugin_manager.load_plugins()
        self.plugins_label.configure(text=f"Plugins chargés: {', '.join(self.plugin_manager.plugin_names)}")

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(header, text="Demo CustomTkinter", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, padx=(10, 5), pady=10)

        version_label = ctk.CTkLabel(header, text=f"Version {__version__}")
        version_label.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="e")

        self.plugin_frame = ctk.CTkFrame(self)
        self.plugin_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        footer = ctk.CTkFrame(self)
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        footer.grid_columnconfigure(0, weight=1)

        self.plugins_label = ctk.CTkLabel(footer, text="Plugins chargés: Aucun")
        self.plugins_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        update_button = ctk.CTkButton(footer, text="Rechercher des mises à jour", command=self._run_update_async)
        update_button.grid(row=0, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(footer, text="Idle")
        self.status_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

    def _run_update_async(self) -> None:
        thread = threading.Thread(target=self.auto_updater.run_update_flow, daemon=True)
        thread.start()


def main() -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
