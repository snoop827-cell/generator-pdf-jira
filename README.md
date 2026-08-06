# Jira Card Generator

Application web de generation de cartes imprimables a partir d'un export CSV Jira.

Le projet est construit progressivement. Cette premiere etape met en place le moteur metier pur, sans dependance a FastAPI ni a une interface utilisateur.

## Objectif

- Lire un export CSV Jira.
- Detecter les colonnes utiles avec tolerance sur la casse, les accents, les espaces et certains synonymes.
- Nettoyer les donnees.
- Regrouper les tickets par Feature, via la cle parent.
- Paginer les cartes selon les regles d'impression A4.
- Generer un PDF A4 par Feature.
- Generer une archive ZIP contenant les PDF.
- Exposer une API FastAPI autour du moteur.
- Produire des modeles metier reutilisables par une API, une CLI ou un script.
- Calculer une couleur stable et deterministe par Feature.

## Architecture

```text
jira-card-generator/
  backend/
    api/         Endpoints FastAPI et adaptation HTTP
    colors/      Couleurs stables par Feature
    core/        Modeles et exceptions metier
    csv/         Lecture, nettoyage et mapping CSV Jira
    layout/      Regles de pagination imprimable
    pdf/         Generation PDF ReportLab
    services/    Cas d'utilisation metier
    tests/       Tests unitaires
  docs/
  docker/
  frontend/
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Les dependances PDF seront ajoutees dans une etape ulterieure :

```powershell
python -m pip install -e ".[dev,pdf]"
```

## Tests

```powershell
python -m pytest
```

## API locale

Demarrer le backend :

```powershell
python -m uvicorn backend.api.main:app --reload
```

Endpoints disponibles :

- `GET /health`
- `POST /api/csv/analyze`
- `POST /api/generate/summary`
- `POST /api/generate`

## Contraintes de conception

- Le moteur metier ne depend pas de FastAPI, React ou ReportLab.
- Les traitements sont deterministes.
- Le regroupement se fait obligatoirement par cle parent.
- La pagination limite chaque page A4 a 8 cartes.
- La premiere page contient 1 carte Feature puis jusqu'a 7 User Stories.
- Les pages suivantes contiennent jusqu'a 8 User Stories.
- Les cartes PDF mesurent 9 cm x 6 cm.
- L'archive ZIP contient les PDF tries par nom de fichier pour garder un resultat stable.
- La couleur d'une Feature est calculee depuis un hash stable de sa cle.

## Deroule de versionnement Git

Le projet est versionne des sa creation.

Principe de travail :

1. Une etape fonctionnelle est developpee dans le code.
2. Les tests associes sont executes.
3. Le resultat est presente pour validation.
4. Apres validation, un commit Git est cree pour figer l'etape.

Convention de commits proposee :

```text
feat: initialiser le socle metier
feat: ajouter la pagination des cartes
feat: ajouter le moteur pdf
feat: ajouter l api fastapi
feat: ajouter l interface web
docs: documenter le deploiement synology
```

Avant chaque commit, verifier :

```powershell
git status
python -m pytest
```

Puis creer le commit :

```powershell
git add .
git commit -m "feat: initialiser le socle metier"
```

## Hebergement Synology

L'application devra pouvoir etre hebergee sur un NAS Synology. Les choix techniques devront donc rester compatibles avec un deploiement Docker.

Objectif de deploiement cible :

- un conteneur backend FastAPI ;
- un frontend servi sous forme de fichiers statiques ou via un conteneur dedie selon la stack du portail existant ;
- un volume persistant pour les fichiers temporaires si necessaire ;
- aucune dependance a un service d'IA ou a une API externe pour la generation.

La documentation de deploiement Synology sera detaillee dans `docs/synology.md`.

## Prochaines etapes

1. Affiner le rendu PDF avec les modeles `Feature.pdf` et `UserStory.pdf`.
2. Integrer le frontend dans la stack du portail existant.
3. Completer Docker et la documentation de deploiement Synology.
