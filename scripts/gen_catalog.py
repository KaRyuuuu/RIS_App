"""Génération du fichier catalog.json à partir des métadonnées locales."""

from __future__ import annotations

import json
from pathlib import Path

from ris_app import __version__
from ris_app.config import CATALOG_CACHE_PATH, PLUGINS_DIR


def load_plugin_metadata(plugin_dir: Path) -> dict[str, str]:
    """Charge le ``plugin.json`` d'un plugin et retourne un dictionnaire minimal."""

    data = json.loads((plugin_dir / "plugin.json").read_text(encoding="utf-8"))
    slug = data["slug"]
    version = data["version"]
    return {
        "slug": slug,
        "version": version,
        "zip_url": data.get("zip_url") or generate_plugin_url(slug, version),
        "sha256": data.get("sha256", ""),
    }


def generate_plugin_url(slug: str, version: str) -> str:
    """Construit l'URL attendue pour un plugin dans les releases GitHub."""

    release_tag = f"v{__version__}"
    return (
        "https://github.com/KaRyuuuuuu/RIS_app/releases/download/"
        f"{release_tag}/plugin_{slug}_{version}.zip"
    )


def build_catalog() -> dict[str, object]:
    """Assemble le contenu du catalogue."""

    plugins = []
    for plugin_json in PLUGINS_DIR.glob("*/plugin.json"):
        plugins.append(load_plugin_metadata(plugin_json.parent))

    release_tag = f"v{__version__}"
    return {
        "core": {
            "version": __version__,
            "zip_url": (
                "https://github.com/KaRyuuuuuu/RIS_app/releases/download/"
                f"{release_tag}/ris_app_core_{__version__}.zip"
            ),
            "sha256": "",
        },
        "plugins": plugins,
    }


def main() -> None:
    catalog = build_catalog()
    CATALOG_CACHE_PATH.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Catalogue généré dans {CATALOG_CACHE_PATH}")


if __name__ == "__main__":
    main()
