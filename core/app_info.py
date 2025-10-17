"""
core/app_info.py
Centralise les infos de l'application (version, chemins...).
"""

from __future__ import annotations
import os
import configparser

# 👉 Mets à jour la version ici (ou lis-la depuis un __init__.py si tu préfères)
APP_VERSION = "1.0"

# Fichier de config utilisateur (persistant)
SETTINGS_FILE = "settings.ini"

def read_settings() -> configparser.ConfigParser:
    """
    Charge (et crée si besoin) le fichier settings.ini.
    Retourne un objet ConfigParser prêt à l'emploi.
    """
    cfg = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        cfg.read(SETTINGS_FILE, encoding="utf-8")
    if "general" not in cfg:
        cfg["general"] = {}
    if "download" not in cfg:
        cfg["download"] = {"default_server": ""}  # vide par défaut
    return cfg

def write_settings(cfg: configparser.ConfigParser) -> None:
    """
    Sauvegarde le fichier settings.ini.
    """
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

def get_app_version() -> str:
    """
    Retourne la version de l'app (affichée dans Paramètres).
    """
    return APP_VERSION
