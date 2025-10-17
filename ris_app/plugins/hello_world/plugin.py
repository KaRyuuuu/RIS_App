"""Plugin Hello World fournissant une commande simple."""

from __future__ import annotations

from ris_app.core.plugin_base import IPlugin


class HelloWorldPlugin(IPlugin):
    """Plugin d'exemple affichant un message de bienvenue."""

    name = "Hello World"
    slug = "hello_world"
    version = "1.0.0"
    author = "KaRyuu"
    description = "Plugin de démonstration."

    def commands(self):  # type: ignore[override]
        return {"say_hello": self.say_hello}

    def say_hello(self, *args: str) -> None:
        """Affiche un message de salutation dans la console."""

        message = " ".join(args) if args else "Bonjour depuis HelloWorldPlugin!"
        print(message)
