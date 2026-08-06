# Architecture

## Separation des responsabilites

- `backend/api` expose le moteur via HTTP avec FastAPI.
- `backend/core` contient uniquement les modeles et erreurs du domaine.
- `backend/csv` transforme un export Jira en objets metier valides.
- `backend/services` orchestre les cas d'utilisation purs, comme le regroupement par Feature.
- `backend/colors` contient les regles deterministes de couleur.
- `backend/layout` contient les regles de pagination imprimable, sans dependance au moteur PDF.
- `backend/pdf` transforme les pages metier en fichiers PDF A4 imprimables.

Le moteur metier reste independant de FastAPI, React, ReportLab et du systeme de fichiers, sauf au point d'entree explicite de lecture CSV.

## Pagination metier

La pagination est modelisee avant la generation PDF pour etre testable sans rendu graphique.

Regles implementees :

- un PDF par Feature ;
- 8 cartes maximum par page A4 ;
- premiere page : 1 carte Feature puis jusqu'a 7 User Stories ;
- pages suivantes : jusqu'a 8 User Stories ;
- conservation stricte de l'ordre des tickets ;
- controle qu'aucune User Story n'est perdue ou dupliquee.

## Generation PDF

Le moteur PDF consomme les objets de pagination. Il ne lit pas directement le CSV et ne regroupe pas les tickets.

Les modeles Photoshop fournis sont conserves dans `docs/templates/` comme reference graphique. Le rendu final reste implemente en ReportLab afin de garder une generation deterministe et sans dependance a Photoshop au runtime.

Regles implementees :

- format A4 ;
- grille fixe de 2 colonnes par 4 lignes ;
- cartes de 9 cm x 6 cm ;
- reperes de coupe autour de la grille pour faciliter l'alignement au massicot ;
- mode noir et blanc avec contour fin de decoupe ;
- mode couleur avec contour plein de 3 mm ;
- couleur stable derivee de la cle Feature.

## Generation ZIP

La creation de l'archive est separee du rendu PDF.

Regles implementees :

- refus d'une archive vide ;
- controle de l'existence de chaque PDF ;
- tri des PDF par nom de fichier avant ajout a l'archive ;
- conservation des noms de fichiers sans chemin local dans l'archive.

## API

La couche API reste volontairement fine.

Endpoints :

- `GET /health` pour les controles d'exploitation ;
- `POST /api/csv/analyze` pour analyser un CSV sans generer les PDF ;
- `POST /api/generate/summary` pour tester la generation et obtenir les compteurs ;
- `POST /api/generate` pour produire l'archive ZIP.

La couche API ne contient pas de regles metier de parsing, regroupement, pagination ou rendu PDF.
