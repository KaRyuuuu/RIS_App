# Application CustomTkinter avec plugin et mise à jour automatique

Cette application démontre comment combiner [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) avec un système de plugins simple et un mécanisme de mise à jour automatique basé sur un manifeste.

## Fonctionnalités
- Interface graphique réalisée avec CustomTkinter.
- Chargement automatique des plugins présents dans `app/plugins`.
- Plugin d'exemple affichant un message de bienvenue et un compteur.
- Vérification et application d'une mise à jour à partir d'un manifeste JSON local.

## Installation
1. Créez un environnement virtuel et activez-le.
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation
Exécutez l'application avec :
```bash
python -m app.main
```

Le bouton "Rechercher des mises à jour" lance le processus automatique :
1. Lecture du manifeste `resources/update_manifest.json`.
2. Si une version plus récente est disponible, téléchargement de l'archive indiquée (support des chemins locaux relatifs ou absolus, ainsi que des URLs HTTP/HTTPS).
3. Extraction de l'archive dans le répertoire racine de l'application.

Pour tester le scénario hors-ligne, générez l'archive de démonstration à l'aide du script fourni :

```bash
python scripts/create_demo_update.py
```

Le script crée `updates/update_1.0.1.zip`, contenant une version 1.0.1 du fichier `app/version.py`. Le manifeste pointe vers cette archive via un chemin relatif ; lancez ensuite l'application et utilisez le bouton "Rechercher des mises à jour" pour vérifier le processus complet.

## Créer vos propres plugins
1. Ajoutez un fichier Python dans `app/plugins`.
2. Définissez une classe qui hérite de `app.plugin_base.Plugin`.
3. Implémentez les méthodes `load` (création des widgets) et `unload` (nettoyage des ressources).

La découverte des plugins est dynamique : tout nouveau module respectant cette interface sera automatiquement chargé au démarrage de l'application.
