# Architecture

## Separation des responsabilites

- `backend/core` contient uniquement les modeles et erreurs du domaine.
- `backend/csv` transforme un export Jira en objets metier valides.
- `backend/services` orchestre les cas d'utilisation purs, comme le regroupement par Feature.
- `backend/colors` contient les regles deterministes de couleur.

Le moteur metier reste independant de FastAPI, React, ReportLab et du systeme de fichiers, sauf au point d'entree explicite de lecture CSV.

