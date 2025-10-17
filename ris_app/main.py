"""Point d'entrée de la ligne de commande ``ris``."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, List

from . import __version__
from .core.plugin_manager import PluginManager
from .core.updater import UpdateError, Updater
from .utils import get_logger

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Construit et retourne l'analyseur de ligne de commande."""

    parser = argparse.ArgumentParser(
        prog="ris",
        description="RIS_app - plateforme modulaire avec système de plugins",
    )
    parser.add_argument("--version", action="version", version=f"RIS_app {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="Affiche les plugins disponibles")

    enable_parser = subparsers.add_parser("enable", help="Active un plugin")
    enable_parser.add_argument("slug", help="Identifiant du plugin")

    disable_parser = subparsers.add_parser("disable", help="Désactive un plugin")
    disable_parser.add_argument("slug", help="Identifiant du plugin")

    run_parser = subparsers.add_parser("run", help="Exécute une commande d'un plugin")
    run_parser.add_argument("slug", help="Identifiant du plugin")
    run_parser.add_argument("plugin_command", help="Commande du plugin à exécuter")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments supplémentaires")

    update_parser = subparsers.add_parser("update", help="Gestion des mises à jour")
    update_sub = update_parser.add_subparsers(dest="update_command", required=True)

    update_check = update_sub.add_parser("check", help="Vérifie la disponibilité de mises à jour")
    update_check.add_argument(
        "--offline",
        action="store_true",
        help="Utilise uniquement le catalogue local sans télécharger",
    )

    update_apply = update_sub.add_parser("apply", help="Télécharge et installe les mises à jour")
    update_apply.add_argument("--core", action="store_true", help="Met à jour le coeur de l'application")
    update_apply.add_argument(
        "--plugins",
        nargs="*",
        help="Liste de plugins à mettre à jour (vide = tous)",
    )
    update_apply.add_argument(
        "--no-new-plugins",
        action="store_true",
        help="N'installe pas automatiquement les nouveaux plugins",
    )

    return parser


def handle_list(manager: PluginManager) -> int:
    """Affiche les informations de base sur tous les plugins."""

    print("Plugins disponibles :")
    for metadata in manager.list_plugins():
        status = "activé" if metadata.slug in manager.plugins else "désactivé"
        print(f" - {metadata.name} ({metadata.slug}) v{metadata.version} - {status}")
        print(f"   Auteur : {metadata.author}")
        if metadata.description:
            print(f"   Description : {metadata.description}")
        plugin = manager.get_plugin(metadata.slug)
        if plugin:
            commands = ", ".join(plugin.get_commands_dict().keys()) or "(aucune commande)"
            print(f"   Commandes : {commands}")
        print()
    return 0


def handle_enable(manager: PluginManager, slug: str) -> int:
    if manager.enable(slug):
        print(f"Plugin '{slug}' activé avec succès.")
        return 0
    return 1


def handle_disable(manager: PluginManager, slug: str) -> int:
    if manager.disable(slug):
        print(f"Plugin '{slug}' désactivé.")
        return 0
    return 1


def handle_run(manager: PluginManager, slug: str, command: str, args: Iterable[str]) -> int:
    if manager.run_command(slug, command, *args):
        return 0
    return 1


def handle_update_check(updater: Updater, *, offline: bool) -> int:
    try:
        catalog = updater.load_local_catalog() if offline else updater.download_catalog()
        updates = updater.check_updates(catalog)
    except UpdateError as exc:
        logger.error(str(exc))
        return 1

    if not updates:
        print("Tout est à jour !")
        return 0

    print("Mises à jour disponibles :")
    for item, version in updates.items():
        print(f" - {item}: {version}")
    return 0


def handle_update_apply(
    updater: Updater,
    catalog,
    *,
    update_core: bool,
    plugins: List[str] | None,
    include_new_plugins: bool,
) -> int:
    try:
        updated_paths = updater.apply_updates(
            catalog,
            core=update_core,
            plugins=plugins,
            include_new_plugins=include_new_plugins,
        )
    except UpdateError as exc:
        logger.error(str(exc))
        return 1

    if not updated_paths:
        print("Aucune mise à jour appliquée (tout était déjà à jour).")
    else:
        print("Mises à jour appliquées sur :")
        for path in updated_paths:
            print(f" - {path}")
        print("Redémarrez l'application si le coeur a été mis à jour.")
    return 0


def main(argv: List[str] | None = None) -> int:
    """Point d'entrée principal de la CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    manager = PluginManager()
    updater = Updater(manager)

    if args.command == "list":
        return handle_list(manager)
    if args.command == "enable":
        return handle_enable(manager, args.slug)
    if args.command == "disable":
        return handle_disable(manager, args.slug)
    if args.command == "run":
        return handle_run(manager, args.slug, args.plugin_command, args.args)
    if args.command == "update":
        if args.update_command == "check":
            return handle_update_check(updater, offline=args.offline)
        if args.update_command == "apply":
            catalog = updater.load_local_catalog()
            if not catalog:
                print("Catalogue indisponible. Lancez 'ris update check' pour le télécharger.")
                return 1
            return handle_update_apply(
                updater,
                catalog,
                update_core=args.core,
                plugins=args.plugins,
                include_new_plugins=not args.no_new_plugins,
            )

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
