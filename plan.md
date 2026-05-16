# Plan : Simplification Nation Wars — Mode Enfant Web

## TL;DR
Transformer Nation Wars d'un jeu standalone APK en un mini-jeu **web pur** ultra-épuré intégrable dans une app tierce. Supprimer tout ce qui est APK/Capacitor/Android. Supprimer toute friction UI (choix de nations, stats, médailles, éditeur, sauvegardes, settings). Assigner automatiquement le pays le plus fort à l'enfant avec feedback visuel. Désactiver la musique, garder uniquement les sons d'ambiance/SFX. Conserver la logique interne de skip (2×S consécutifs).

---

## Phase 0 — Suppression APK / Capacitor / Android (tout ce qui n'est pas le jeu web)

### 0.1 Supprimer les dossiers entiers
- **Supprimer** `android/` (tout le projet Android/Capacitor)
- **Supprimer** `web/` (dossier output Capacitor)
- **Supprimer** `scripts/` (contient uniquement `prepare-web.mjs` pour Capacitor)

### 0.2 Supprimer les fichiers de config/build mobile
- **Supprimer** `capacitor.config.json`
- **Supprimer** `ANDROID_SETUP.md`
- **Supprimer** `lancer_serveur_mobile.bat`
- **Supprimer** `lancer_serveur_mobile.ps1`
- **Supprimer** `ouvrir_android.bat`
- **Supprimer** `sync_android.bat`

### 0.3 Nettoyer `package.json`
- Supprimer les dépendances : `@capacitor/android`, `@capacitor/cli`, `@capacitor/core`
- Supprimer les scripts : `build:web`, `cap:sync`, `android:add`, `android:open`
- Si package.json devient vide (pas d'autre dépendance utile), le supprimer aussi

---

## Phase 1 — Suppression des éléments UI superflus (dans index.html)

### 1.1 Supprimer l'éditeur de niveau
- **Supprimer** `editeur.html` (racine)

### 1.2 Supprimer l'écran de sauvegardes
- Supprimer le `#save-panel` entier dans `index.html`
- Supprimer tout le JS associé (slots, localStorage save/load/delete)

### 1.3 Supprimer l'écran de choix de nations (`#country-select`)
- Supprimer le HTML de `#country-select`
- Supprimer le JS de sélection manuelle de pays
- Remplacer par la logique auto (Phase 2)

### 1.4 Supprimer les stats de fin de partie
- Supprimer la grille de 8 stats du `#end-screen`
- Supprimer le bloc "Recent history"
- Supprimer le guide des médailles (`#medal-guide`)
- Simplifier l'écran de fin : garder uniquement Victoire/Défaite + Grade + bouton Suivant

### 1.5 Supprimer les médailles de la sélection de niveaux
- Retirer les icônes médailles (⚡👑🛡️🚩) des cartes de niveau
- Retirer le temps personnel (best time) des cartes
- Simplifier les cartes : numéro + état (débloqué/verrouillé/complété) + grade obtenu

### 1.6 Supprimer le panneau Settings
- Supprimer `#settings-overlay` entièrement
- Garder uniquement un bouton Home (retour menu) dans le HUD en jeu

---

## Phase 2 — Attribution automatique du pays le plus fort + annonce visuelle

### 2.1 Logique d'auto-sélection
- Au lancement d'un niveau, parcourir `level.countries` où `ownerId === 1` (joueur)
- Sélectionner le pays avec le score le plus élevé : `unitsPrecise * populationTierMultiplier`
- Si un seul pays joueur, le prendre directement

### 2.2 Écran d'introduction "Vous êtes [Pays]" (~3s)
- Texte centré animé : "Vous êtes la **France** 🇫🇷"
- Effet visuel très marqué sur le pays dans le canvas : pulse/glow lumineux animé sur le polygone
- Transition automatique vers le gameplay après l'animation

---

## Phase 3 — Simplification de la grille de niveaux

### 3.1 Refonte de la grille `#level-select`
- Carrés plus petits, grille compacte (5×4), tout visible sans scroll
- Chaque carré : numéro + couleur d'état (gris=verrouillé, vert=complété, bleu=disponible)
- Grade S montré par une étoile dorée discrète

### 3.2 API d'ouverture directe (mode intégré)
- Paramètre URL `index.html?level=5` pour ouvrir directement un niveau
- Skip total du menu si paramètre présent

---

## Phase 4 — Audio : désactiver musique, garder SFX/ambiance

### 4.1 Désactiver la musique
- Supprimer ou commenter le chargement de `maintheme.mp3`
- Supprimer toute référence au toggle/volume musique
- Ne pas supprimer le fichier mp3 (au cas où), juste ne plus le charger

### 4.2 Garder les sons d'ambiance/SFX
- Conserver tous les sons de jeu (attaques, conquêtes, victoire, défaite, etc.)
- Volume SFX fixé à une valeur par défaut raisonnable (pas de slider)

---

## Phase 5 — Conservation logique de skip + callback app parent

### 5.1 Maintenir grade + skip
- Garder le calcul de grade (S/A/B/C/D) et la règle 2×S consécutifs → niveau N+2

### 5.2 Callback vers l'app parent
- Émettre `postMessage` après chaque partie : `{ level, grade, time, victory, skipped }`

---

## Phase 6 — Nettoyage final

### 6.1 Nettoyage i18n.js
- Supprimer clés inutiles (médailles, stats, save, settings, éditeur)
- Ajouter clé `"you_are_country"`

### 6.2 Nettoyage CSS dans index.html
- Supprimer styles des éléments supprimés
- Adapter la grille au format compact

### 6.3 Nettoyage sw.js
- Retirer `editeur.html` du cache si listé
- Retirer les références aux fichiers supprimés

---

## Fichiers à SUPPRIMER

| Fichier/Dossier | Raison |
|---|---|
| `android/` (tout le dossier) | Projet APK Capacitor |
| `web/` (tout le dossier) | Output Capacitor |
| `scripts/` (tout le dossier) | Build helper Capacitor |
| `capacitor.config.json` | Config Capacitor |
| `ANDROID_SETUP.md` | Doc APK |
| `lancer_serveur_mobile.bat` | Script mobile |
| `lancer_serveur_mobile.ps1` | Script mobile |
| `ouvrir_android.bat` | Script Android |
| `sync_android.bat` | Script Android |
| `editeur.html` | Éditeur de niveaux |

## Fichiers à MODIFIER

| Fichier | Modifications |
|---|---|
| `index.html` | Supprimer #country-select, #save-panel, #settings-overlay, #medal-guide, stats #end-screen. Simplifier #level-select. Ajouter écran annonce pays. Ajouter API ?level=N. Désactiver musique. Supprimer boutons éditeur/save. |
| `i18n.js` | Supprimer clés inutiles, ajouter `you_are_country` |
| `sw.js` | Retirer fichiers supprimés du cache |
| `package.json` | Supprimer dépendances/scripts Capacitor (ou supprimer le fichier si vide) |

## Fichiers CONSERVÉS tels quels

| Fichier | Rôle |
|---|---|
| `levels.js` | Données des 20 niveaux (inchangé) |
| `manifest.webmanifest` | PWA manifest |
| `img/` | Images/maps du jeu |
| `GDD_Nation_Wars_2_v1.3_FINAL.md` | Game Design Document (référence) |

---

## Vérification

1. Plus aucun dossier `android/`, `web/`, `scripts/` ni fichier `.bat`/`.ps1`/`capacitor.*`
2. Ouvrir `index.html` → grille compacte sans scroll, pas de bouton éditeur/save/settings
3. Cliquer un niveau → écran "Vous êtes la France 🇫🇷" avec glow animé, PAS de choix de nation
4. Le jeu se lance auto après ~3s, PAS de musique, sons d'ambiance OK
5. Fin de partie → Victoire/Défaite + Grade + bouton Suivant uniquement
6. 2×S consécutifs → skip fonctionne
7. `index.html?level=5` → niveau 5 se lance directement
8. Test mobile : tout visible sans scroll

## Décisions

- Musique désactivée, SFX/ambiance conservés à volume fixe
- Tout Capacitor/Android/APK supprimé — version web pure uniquement
- Éditeur supprimé
- Sauvegardes supprimées — l'app parent gère la progression
- Choix de nation → auto-assignation du plus fort avec annonce visuelle
- Stats/médailles supprimées de l'UI, logique de grade conservée
- Communication app parent via `postMessage`
- Bouton Home conservé en jeu pour retour grille
