"""Tests basiques pour vérifier le chargement des plugins."""

from __future__ import annotations

from ris_app.core.plugin_manager import PluginManager


def test_plugins_load_and_commands(capsys):
    """Vérifie que les plugins d'exemple sont chargés et que leurs commandes fonctionnent."""

    manager = PluginManager()
    assert manager.get_plugin("hello_world") is not None

    manager.run_command("hello_world", "say_hello", "PyTest")
    captured = capsys.readouterr()
    assert "PyTest" in captured.out

    # Le plugin sample_ris_tool est désactivé par défaut : activation nécessaire.
    manager.enable("sample_ris_tool")
    manager.run_command("sample_ris_tool", "parse_live_xml", "faux.xml")
    captured = capsys.readouterr()
    assert "introuvable" in captured.out
