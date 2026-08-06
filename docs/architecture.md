# Architecture

## Separation des responsabilites

- `backend/core` contient uniquement les modeles et erreurs du domaine.
- `backend/csv` transforme un export Jira en objets metier valides.
- `backend/services` orchestre les cas d'utilisation purs, comme le regroupement par Feature.
- `backend/colors` contient les regles deterministes de couleur.
- `backend/layout` contient les regles de pagination imprimable, sans dependance au moteur PDF.

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
