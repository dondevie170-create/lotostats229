# LotoStats229 — Pipeline automatique

Automatise entièrement : récupération des tirages → calcul des tendances →
mise à jour du site → publication Telegram.

## Structure

```
scripts/
  scraper.py        # récupère les tirages depuis lnbloto.bj/results
  analyze.py         # calcule tendances, écarts, 2 Nap / 3 Nap
  generate_site.py   # génère site/index.html
  telegram_post.py   # publie la tendance du jour sur Telegram
data/
  tirages.json        # base de données (créée/mise à jour automatiquement)
  tendances.json       # résultat du calcul (créé automatiquement)
site/
  index.html           # page générée automatiquement
.github/workflows/
  update.yml            # orchestration automatique (GitHub Actions)
```

## Mise en route (à faire une seule fois)

### 1. Créer le dépôt GitHub
- Crée un dépôt GitHub **public** (gratuit, minutes GitHub Actions illimitées
  pour les dépôts publics — à vérifier sur ton compte car les conditions
  peuvent évoluer).
- Mets-y ce dossier complet.

### 2. Récupérer les données déjà accumulées
Le fichier `data/tirages.json` fourni contient déjà les 265 tirages qu'on
a analysés ensemble (18 août → 2 octobre 2026). Il sert de point de départ
pour que l'historique ne reparte pas de zéro.

### 3. Créer le bot Telegram
1. Dans Telegram, cherche **@BotFather**
2. Envoie `/newbot`, choisis un nom (ex: LotoStats229Bot)
3. Récupère le **token** qu'il te donne
4. Ajoute ce bot comme **administrateur** de ton canal LotoStats229
5. Récupère l'identifiant du canal (son `@nomdutilisateur` s'il est public)

### 4. Configurer les secrets GitHub
Dans le dépôt GitHub : **Settings → Secrets and variables → Actions → New repository secret**
- `TELEGRAM_BOT_TOKEN` = le token de l'étape 3
- `TELEGRAM_CHAT_ID` = l'identifiant du canal (ex: `@lotostats229`)

### 5. Activer l'hébergement du site
- Sur **Vercel** ou **Netlify** (gratuits) : connecte le dépôt GitHub, pointe
  vers le dossier `site/`. Chaque mise à jour automatique du dépôt redéploiera
  le site tout seul.
- Alternative encore plus simple : **GitHub Pages** (Settings → Pages →
  source = dossier `site/`).

### 6. Premier test manuel
Avant de laisser tourner automatiquement : va dans l'onglet **Actions** du
dépôt GitHub, sélectionne le workflow "Mise à jour LotoStats229", et clique
**Run workflow** pour le lancer manuellement une première fois. Vérifie que :
- le scraping fonctionne (sinon, il faudra ajuster la regex dans `scraper.py`
  selon la structure réelle de la page au moment du test)
- le message arrive bien sur Telegram
- le site se régénère correctement

### 7. Laisser tourner
Une fois le test validé, le `cron` dans `update.yml` prend le relais : le
pipeline se déclenche automatiquement après chaque heure de tirage.

## Point de vigilance
Vérifier les conditions d'utilisation du site de la Loterie Nationale avant
de lancer le scraping automatique en continu, pour éviter tout souci de
conformité.
