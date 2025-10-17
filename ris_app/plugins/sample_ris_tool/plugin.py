"""Plugin d'exemple pour illustrer un outil RIS."""

from __future__ import annotations

from pathlib import Path

from ris_app.core.plugin_base import IPlugin


class SampleRISToolPlugin(IPlugin):
    """Plugin fictif qui démonte le fonctionnement général d'un outil RIS."""

    name = "Sample RIS Tool"
    slug = "sample_ris_tool"
    version = "0.5.0"
    author = "KaRyuu"
    description = "Exemple de plugin simulant un outil RIS."

    def commands(self):  # type: ignore[override]
        return {"parse_live_xml": self.parse_live_xml}

    def parse_live_xml(self, path: str) -> None:
        """Analyse un fichier XML (simulation)."""

        xml_path = Path(path)
        if not xml_path.exists():
            print(f"Fichier {xml_path} introuvable. Placez un fichier de test pour la démo.")
            return
        print(f"Simulation d'analyse du fichier {xml_path}... Terminé !")
