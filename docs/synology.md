# Deploiement Synology

Cette application devra etre deployable sur un NAS Synology, idealement via Docker ou Container Manager.

## Principes retenus

- Packaging Docker des composants applicatifs.
- Configuration par variables d'environnement.
- Generation deterministe realisee localement dans le backend.
- Aucun appel a un service d'IA ou a une API externe pour produire les PDF.
- Possibilite de monter un volume pour les fichiers temporaires et les journaux.

## Architecture cible

```text
Synology NAS
  Container Manager / Docker
    backend FastAPI
    frontend React/Vite servi par nginx
    volume temporaire pour generations
```

## Deploiement backend avec Container Manager

Depuis le NAS ou une machine ayant acces au Docker du NAS :

```bash
docker compose -f docker/docker-compose.synology.yml up -d --build
```

Controle de sante :

```bash
curl http://IP_DU_NAS:8000/health
```

Reponse attendue :

```json
{"status":"ok"}
```

Interface web :

```text
http://IP_DU_NAS:8080/jira-cards/
```

## Points a preciser lors des prochaines etapes

- Stack exacte du portail existant.
- Mode d'integration frontend attendu.
- Methode actuelle de deploiement sur le NAS.
- Nom de domaine ou reverse proxy Synology deja utilise.
- Gestion HTTPS actuelle.

## Variables d'environnement pressenties

```text
APP_ENV=production
APP_TMP_DIR=/tmp/jira-card-generator
APP_MAX_UPLOAD_MB=25
```

Ces variables sont deja declarees dans le `docker-compose` backend. Elles pourront etre completees quand le frontend sera integre au portail.
