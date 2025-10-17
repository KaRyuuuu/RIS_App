"""Utilitaire de journalisation léger pour l'application.

Les applications distribuées doivent fournir un feedback clair à l'utilisateur. Ce module
configure un logger basé sur :mod:`logging` avec un format simple et lisible.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from ..config import LOGGER_NAME


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Retourne un logger configuré.

    Parameters
    ----------
    name:
        Nom du logger. Si ``None``, nous utilisons le nom global de l'application défini dans
        :mod:`ris_app.config`.
    """

    logger_name = name or LOGGER_NAME
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        # Configuration initiale du logger uniquement lors de la première utilisation. Cela évite
        # de dupliquer les handlers si ``get_logger`` est appelé plusieurs fois.
        level_name = os.getenv("RIS_APP_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        logger.setLevel(level)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
