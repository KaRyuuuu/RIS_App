# RIS_app

RIS_app est une application Python modulaire pensée pour héberger des outils RIS (Radiology Information System) via un système de plugins simple. Elle est fournie prête à l'emploi avec un pipeline CI/CD qui génère automatiquement les archives et le catalogue de mise à jour lors de chaque publication GitHub.

## Sommaire

1. [Prérequis](#prérequis)
2. [Installation locale](#installation-locale)
3. [Utilisation de la CLI](#utilisation-de-la-cli)
4. [Organisation du projet](#organisation-du-projet)
5. [Créer un plugin](#créer-un-plugin)
6. [Système de mises à jour](#système-de-mises-à-jour)
7. [Pipeline GitHub Actions](#pipeline-github-actions)
8. [Tests et qualité](#tests-et-qualité)
9. [Génération du catalogue](#génération-du-catalogue)
10. [FAQ pour débutants](#faq-pour-débutants)

## Prérequis

- Python 3.11 ou supérieur
- `pip` récent
- Accès à internet pour les mises à jour automatiques

## Installation locale

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/KaRyuuuuuu/RIS_app.git
   cd RIS_app
   ```
2. Créez un environnement virtuel (fortement recommandé) :
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
   ```
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Installez l'application en mode développement (facultatif mais pratique) :
   ```bash
   pip install -e .
   ```

## Utilisation de la CLI

Exécuter l'application :
```bash
python -m ris_app --help
```

Commandes principales :
- `ris list` : liste les plugins disponibles, leur version et leurs commandes.
- `ris enable <slug>` / `ris disable <slug>` : active ou désactive un plugin.
- `ris run <slug> <commande> [args...]` : exécute une commande exposée par un plugin.
- `ris update check` : télécharge (ou utilise en local) le `catalog.json` pour vérifier les mises à jour.
- `ris update apply [--core] [--plugins <slug...>] [--no-new-plugins]` : applique les mises à jour disponibles.

Chaque commande affiche des messages clairs. En cas d'erreur, le logger intégré fournit des détails utiles.

## Organisation du projet

```
RIS_app/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── ris_app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   ├── config.py
│   ├── utils/
│   │   ├── io.py
│   │   ├── log.py
│   │   └── version.py
│   ├── core/
│   │   ├── plugin_base.py
│   │   ├── plugin_manager.py
│   │   ├── registry.py
│   │   └── updater.py
│   ├── data/
│   │   ├── catalog.json
│   │   └── registry.json
│   └── plugins/
│       ├── hello_world/
│       └── sample_ris_tool/
├── scripts/
│   └── gen_catalog.py
├── tests/
│   └── test_plugins.py
└── .github/workflows/build-release.yml
```

### Dossiers importants
- `ris_app/core/` : coeur applicatif (plugin manager, registre, updater).
- `ris_app/plugins/` : plugins embarqués. Chaque dossier contient un `plugin.json` et un module Python.
- `ris_app/data/` : fichiers persistants (`registry.json`) et cache du catalogue (`catalog.json`).
- `scripts/` : scripts utilitaires (génération du catalogue).
- `tests/` : tests automatisés avec `pytest`.

## Créer un plugin

1. Créez un dossier `ris_app/plugins/mon_plugin/`.
2. Ajoutez un fichier `plugin.json` minimal :
   ```json
   {
     "name": "Mon Plugin",
     "slug": "mon_plugin",
     "version": "0.1.0",
     "author": "Moi",
     "description": "Ce plugin fait quelque chose de génial.",
     "entry": "plugin:MonPlugin",
     "enabled": true
   }
   ```
3. Ajoutez un fichier `__init__.py` vide pour déclarer le package.
4. Créez `plugin.py` et implémentez une classe héritant de `IPlugin` :
   ```python
   from ris_app.core.plugin_base import IPlugin

   class MonPlugin(IPlugin):
       name = "Mon Plugin"
       slug = "mon_plugin"
       version = "0.1.0"
       author = "Moi"
       description = "Ce plugin fait quelque chose de génial."

       def commands(self):  # type: ignore[override]
           return {
               "do_something": self.do_something,
           }

       def do_something(self, *args: str) -> None:
           print("Je fais quelque chose avec", args)
   ```
5. Démarrez l'application et activez le plugin :
   ```bash
   python -m ris_app enable mon_plugin
   python -m ris_app run mon_plugin do_something exemple
   ```

> **Astuce :** Ajoutez votre plugin au dépôt, poussez sur GitHub, et le workflow génèrera automatiquement l'archive ZIP correspondante ainsi que les informations dans `catalog.json`.

## Système de mises à jour

- Le fichier `ris_app/data/catalog.json` est téléchargé depuis la dernière release GitHub (avec fallback sur la branche `main`).
- Le catalogue décrit la version courante du coeur et de chaque plugin, ainsi que l'URL de l'archive ZIP et son empreinte SHA-256.
- `ris update check` compare ces versions avec celles installées localement.
- `ris update apply` télécharge les archives nécessaires, vérifie les empreintes puis extrait les fichiers de manière atomique.
- Les plugins nouvellement listés dans le catalogue sont proposés automatiquement.

## Pipeline GitHub Actions

Le workflow `.github/workflows/build-release.yml` s'exécute sur chaque `push` ou publication de tag `v*` :
1. Installation de Python et des dépendances.
2. Exécution des tests (pytest + ruff).
3. Génération des archives ZIP :
   - `ris_app_core_<version>.zip` pour le coeur (exclut `plugins/`).
   - `plugin_<slug>_<version>.zip` pour chaque plugin.
4. Génération d'un `catalog.json` cohérent.
5. Sur publication de tag `vX.Y.Z`, création d'une release GitHub avec les archives et le catalogue en assets.
6. Sur simple `push`, stockage des mêmes fichiers en artifacts pour vérification.

## Tests et qualité

- Linter : `ruff` (configuré via `pyproject.toml`).
- Tests : `pytest`. Un test d'exemple vérifie que les plugins se chargent et que leurs commandes fonctionnent.

Pour lancer la suite complète :
```bash
ruff check .
pytest
```

## Génération du catalogue

Le script `scripts/gen_catalog.py` lit la version du coeur (`ris_app.__version__`) ainsi que les métadonnées de chaque plugin pour produire un `catalog.json` local. Il est utilisé par le workflow CI mais peut être exécuté manuellement :
```bash
python scripts/gen_catalog.py
```

## FAQ pour débutants

**Où placer mes scripts personnalisés ?**
> Dans un nouveau dossier `ris_app/plugins/<mon_plugin>` contenant au minimum `plugin.json`, `__init__.py` et `plugin.py`.

**Comment activer/désactiver un plugin ?**
> Utilisez `ris enable <slug>` ou `ris disable <slug>`. L'état est mémorisé dans `ris_app/data/registry.json`.

**Comment savoir quelles commandes expose un plugin ?**
> `ris list` affiche toutes les commandes déclarées.

**Puis-je utiliser des bibliothèques tierces ?**
> L'objectif est de rester léger : seules la bibliothèque standard, `requests` et `packaging` sont nécessaires. Vous pouvez ajouter des dépendances via `pyproject.toml` si besoin, mais tenez compte de la portabilité.

Bon développement !
