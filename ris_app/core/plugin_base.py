"""Définition de l'interface de base pour les plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict, Mapping


class IPlugin(ABC):
    """Interface minimale que tous les plugins doivent implémenter.

    Les attributs ``name``, ``version`` et autres sont exposés sous forme de propriétés simples
    pour faciliter l'affichage dans la CLI. Les méthodes ``activate`` et ``deactivate`` sont
    optionnelles : l'implémentation de base n'effectue aucune action, mais les plugins peuvent les
    surcharger pour effectuer des initialisations spécifiques.
    """

    name: str
    version: str
    description: str
    author: str

    def __init__(self) -> None:
        # Les sous-classes peuvent utiliser ``__post_init__`` ou redéfinir ``__init__`` pour
        # préparer leurs ressources. Ici nous ne faisons rien de particulier.
        super().__init__()

    def activate(self) -> None:  # pragma: no cover - implémentation par défaut triviale
        """Prépare le plugin avant son utilisation."""

    def deactivate(self) -> None:  # pragma: no cover - implémentation par défaut triviale
        """Nettoie les ressources du plugin."""

    @abstractmethod
    def commands(self) -> Mapping[str, Callable[..., None]]:
        """Retourne les commandes exposées par le plugin."""

    def get_commands_dict(self) -> Dict[str, Callable[..., None]]:
        """Fournit un dictionnaire modifiable des commandes.

        Les implémentations peuvent retourner n'importe quel objet de type Mapping; nous le
        convertissons en dictionnaire standard pour faciliter son utilisation dans la CLI.
        """

        return dict(self.commands())
