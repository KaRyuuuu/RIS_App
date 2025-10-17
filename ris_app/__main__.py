"""Point d'entrée du module exécutable (``python -m ris_app``)."""

from .main import main


if __name__ == "__main__":
    # Lorsque le package est exécuté comme un module, nous déléguons à la fonction
    # ``main`` définie dans ``ris_app.main``. Cela rend le comportement cohérent avec
    # l'installation d'un script ``ris`` via ``python -m ris_app`` ou via ``pip``.
    main()
