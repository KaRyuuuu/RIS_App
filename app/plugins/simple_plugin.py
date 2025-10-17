"""A simple plugin that displays a greeting and a counter."""
from __future__ import annotations

import customtkinter as ctk

from ..plugin_base import Plugin


class SimpleGreetingPlugin(Plugin):
    name = "Greeting Plugin"

    def __init__(self) -> None:
        self._frame: ctk.CTkFrame | None = None
        self._counter = 0
        self._label: ctk.CTkLabel | None = None

    def load(self, master: "ctk.CTkFrame") -> None:
        self._frame = ctk.CTkFrame(master)
        self._frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = ctk.CTkLabel(self._frame, text="Bonjour !", font=("Arial", 20, "bold"))
        title.pack(pady=(0, 10))

        self._label = ctk.CTkLabel(self._frame, text="Compteur: 0")
        self._label.pack(pady=(0, 10))

        button = ctk.CTkButton(self._frame, text="Incrémenter", command=self.increment)
        button.pack()

    def increment(self) -> None:
        self._counter += 1
        if self._label:
            self._label.configure(text=f"Compteur: {self._counter}")

    def unload(self) -> None:
        if self._frame:
            self._frame.destroy()
            self._frame = None
        self._label = None
        self._counter = 0
