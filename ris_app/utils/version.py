"""Fonctions utilitaires autour des numéros de version."""

from __future__ import annotations

from packaging import version


def parse_version(value: str) -> version.Version:
    """Analyse une chaîne SemVer en objet :class:`packaging.version.Version`."""

    return version.Version(value)


def is_newer(current: str, candidate: str) -> bool:
    """Retourne ``True`` si ``candidate`` est strictement plus récent que ``current``."""

    return parse_version(candidate) > parse_version(current)
