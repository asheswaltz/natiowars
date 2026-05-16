# GDD — Nation Wars 2 (v1.4)
Date: 2026-03-08  
Auteur: mguitter  
Plateforme: Web (HTML/CSS/JavaScript)  
Mode: Solo  
Référence: gameplay type *state.io*  

## 0) Pitch
Jeu de conquête casual: chaque pays produit des unités automatiquement. Le joueur donne des ordres très simples (clic source → clic cible) pour envoyer ses troupes et conquérir tous les pays d’une carte. Campagne 20 niveaux jusqu’aux continents (Europe/Asie/Afrique).

---

## 1) Pilliers
1. **Simple**: 2 clics pour agir, règles lisibles.
2. **Satisfaisant**: accumulation d’unités + conquête rapide.
3. **Lisible**: drapeaux, compteurs, couleurs par propriétaire.
4. **Progressif**: 20 niveaux, difficulté croissante (multi IA, cartes plus grandes).
5. **Immersif**: unités visibles en mouvement (particules).

---

## 2) Mode de jeu & progression
- **Solo uniquement**
- **Progression par niveaux**
  - victoire → niveau suivant
  - défaite → retry ou quitter
- Objectifs de durée:
  - Niveau 1: < 5 minutes
  - Niveau 20: ~ 20 minutes

---

## 3) Contenu (campagne 8 niveaux)
- Niveaux 1–3 : Europe de l'Ouest (3 à 5 pays)
- Niveaux 4–5 : Europe élargie (6 à 9 pays)
- Niveau 6 : Europe du Nord + Centre (Scandinavie, Pologne, etc.)
- Niveaux 7–8 : Afrique (5 à 8+ pays)

### 3.1 Continents: règle de contenu (C1 + regroupement)
- Base: **un pays = un vrai pays** (frontières simplifiées).
- Exception: micro-états peuvent être **regroupés** en “régions”.
  - Ces régions regroupées **n’ont pas de drapeau** (icône neutre à la place).

---

## 4) Représentation visuelle / UI
### 4.1 Carte
- Fond: carte avec **formes des pays** (polygones/paths) simplifiées mais reconnaissables.
- Chaque pays possède un **rond central** (node) placé au `center`.

### 4.2 Node (rond central) par pays
Contient:
- Drapeau du propriétaire (si `flagCode` existe), sinon **icône neutre**
- Compteur d’unités (nombre)

### 4.3 Couleurs de possession
- Le **remplissage du pays** (polygone) dépend de `ownerId`.
- Bordures (stroke) constantes pour garder les frontières lisibles.
- Le remplissage n'est plus totalement statique: une **brillance transparente animée** peut balayer la surface.
- Les pays du joueur sont **plus brillants**, les pays neutres **plus mats**, les IA restent intermédiaires.
- Les frontières peuvent recevoir une **vague lumineuse légère** pour éviter l'effet figé.

### 4.4 HUD minimal
- Boutons: Restart, Quit
- Barre d'armées en temps réel en bas de l'écran, avec répartition visuelle des forces en présence.
- Petit encart HUD dynamique pouvant mettre en avant une statistique live (ex: plus grande armée, forteresse, conquérant en cours).
- Écran de fin: Win (Next), Lose (Retry/Quit)

---

## 5) Input & UX (verrouillé)
### 5.1 Commande principale
- `clic` sur un pays du joueur = **sélection source**
- `clic` sur un autre pays (ou le même) = **cible** → ordre exécuté

### 5.2 Feedback de sélection
Quand une source est sélectionnée:
- **halo/contour** sur le pays source
- **ligne fantôme** du centre de la source vers la position souris (mise à jour en continu)
- clic dans le vide (ou touche ESC si ajoutée): annule

---

## 6) Gameplay (règles figées)
### 6.1 Données
**Country**
- `id`, `name`
- `ownerId`
- `unitsPrecise` (float interne)
- `populationTier` (1..6)
- `center {x,y}`
- `svgPathId`
- `flagCode` (nullable)

**TroopTransfer**
- `fromId`, `toId`, `ownerId`
- `units` (int)
- `travelTime`
- `t` progression 0..1

### 6.2 Génération automatique (population normalisée)
- Multiplicateurs par tiers (défaut):
  - T1 x0.8, T2 x1.0, T3 x1.2, T4 x1.5, T5 x2.0, T6 x2.5
- `spawnRate = baseRate * multiplier(populationTier)`
- Tick:
  - `unitsPrecise += spawnRate * dt`
- Affichage:
  - `unitsDisplayed = floor(unitsPrecise)`

Paramètres par défaut:
- `baseRate = 1.0 unit/s`

### 6.3 Portée d’attaque
- Un pays peut attaquer **n’importe quel pays**.

### 6.4 Envoi “100% mais garde 1”
- `minGarrison = 1`
- Lors d’un ordre:
  - `send = max(0, floor(source.unitsPrecise) - minGarrison)`
  - `source.unitsPrecise -= send`
  - si `send == 0`: pas d’envoi

### 6.5 Déplacement (distance-based)
- `d = distance(source.center, target.center)`
- `travelSpeed = 125 px/s` (défaut)
- `travelTime = d / travelSpeed`
- Update:
  - `t += dt / travelTime`
  - `pos = lerp(from.center, to.center, t)`
- À l’arrivée (`t >= 1`): résolution combat/renfort (ci-dessous)

### 6.6 Combat & capture (à l’arrivée)
- Si même owner:
  - `target.unitsPrecise += transfer.units`
- Sinon:
  - `target.unitsPrecise -= transfer.units`
  - si `target.unitsPrecise < 0`:
    - `target.ownerId = transfer.ownerId`
    - `target.unitsPrecise = abs(target.unitsPrecise)`

### 6.7 Conditions de fin
- Victoire: joueur possède tous les pays
- Défaite: joueur possède 0 pays

---

## 7) Transferts visibles — choix T2 (particules)
### 7.1 Rendu
- Un transfert affiche **plusieurs particules** se déplaçant de source à cible.
- Paramètres recommandés (tunable):
  - `particleCount = clamp(floor(transfer.units / k), minP, maxP)`
  - ex: `k=5`, `minP=6`, `maxP=40`
- Chaque particule:
  - suit la même trajectoire (segment) avec un offset temporel pour créer un flux
  - couleur selon `ownerId`

### 7.2 Objectif
- Donner la sensation que “des unités avancent” vers la destination, sans rendre 1 particule = 1 unité (trop coûteux).

---

## 8) IA (spec v1)
### 8.1 Règles générales
- Les IA jouent avec les **mêmes règles** (spawn, envoi all-but-1, travel).
- En niveaux difficiles: plusieurs IA, **sans équipes**.

### 8.2 Paramètres IA (par IA indépendant)
- Chaque IA (1–4) possède sa **propre config** indépendante :
  ```js
  ai: {
    1: { difficulty, thinkInterval, minUnitsToAttack, focusPlayerWeight },
    2: { ... }, 3: { ... }, 4: { ... }
  }
  ```
- `difficulty`: preset (`tres_facile`, `facile`, `moyen`, `difficile`, `expert`)
- `thinkInterval` (s)
- `minUnitsToAttack`
- `focusPlayerWeight` (0..1)

### 8.3 Décision type
À chaque “think”:
1. lister les pays IA éligibles (`unitsDisplayed >= minUnitsToAttack`)
2. scorer les cibles (toutes les autres):
   - score ↑ si cible faible (`unitsDisplayed` bas)
   - score ↑ si cible appartient au joueur (selon focus)
   - (option) score ↓ si trop loin (distance)
3. choisir la meilleure cible et attaquer

### 8.4 Courbe (paliers)
- N1–5: 1 IA, thinkInterval ~1.2s, minUnitsToAttack ~12, très facile
- N6–10: 1–2 IA, thinkInterval ~1.0s, minUnitsToAttack ~10, facile 
- N11–15: 2–3 IA, thinkInterval ~0.8s, minUnitsToAttack ~9, moyen
- N16–20: 3–4 IA, thinkInterval ~0.6s, minUnitsToAttack ~8, difficile 

---

## 9) Données & formats (JSON)
### 9.1 Niveau
- 1 fichier JSON par niveau: `levels/level_XX.json`
- Référence un SVG: `maps/<name>.svg`
- Contient:
  - `rules` (baseRate, travelSpeed, minGarrison…)
  - `populationTiers`
  - `players` + `ai` params
  - `countries[]` (id, svgPathId, center, populationTier, initialOwner, initialUnits, flagCode?)

### 9.2 Drapeaux (rendu canvas)
- Les drapeaux sont **dessinés directement en canvas** (pas d'assets SVG externes).
- Deux fonctions: `drawFlagRaw()` (troupes, sans clip) et `drawFlag()` (zones, avec rounded rect clip).
- Drapeaux implémentés: `fr`, `gb`, `es`, `pt`, `ie`, `it`, `ch`, `de`, `pl`, `at`, `cz`, `no`, `se`, `fi`, `is`, `mg`, `ma`, `dz`, `za`, `ne`, `ml`, `eg`, `sd`, `re` (La Réunion → tricolore français).
- Si `flagCode` inconnu: rectangle gris + "?".

---

## 9.3 Grades & meilleur temps
- Chaque niveau possède des seuils de grades: `{ S, A, B, C }` (en secondes). Au-delà de C → grade D.
- À la victoire, le temps est enregistré et un grade attribué (S/A/B/C/D).
- `bestTime` sauvegardé en `localStorage` (valeur `99999` = pas encore complété).
- Affichage du grade (S/A/B/C) dans la grille de sélection de niveaux.

## 9.4 Formations de troupes
- Les troupes envoyées adoptent une **formation** basée sur le nombre d'unités envoyées (`send`) :
  - `send ≤ 10` : **file indienne** (1 par 1, départs séquentiels)
  - `send 11–15` : **2 rangées** de front
  - `send 16–20` : **3 rangées** de front
  - `send > 20` : **4 rangées** de front
- Paramètres: `rowGap = 0.22s` (écart temporel entre rangées), `colSpacing = 16px` (écart latéral).
- S'applique au joueur et à l'IA.

## 9.5 Population & tier réalistes
- `unitsPrecise` : proportionnel à la **population réelle** du pays, mis à l'échelle entre **3 et 10**.
- `populationTier` : proportionnel à la **puissance militaire réelle** du pays, mis à l'échelle entre **1 et 5**.
  - Tier 1 (×0.8) : Islande, Madagascar, Niger, Mali, Irlande, RD Congo, Cameroun
  - Tier 2 (×1.0) : Portugal, Suisse, Autriche, Norvège, Suède, Finlande, Tchéquie, Maroc, Kenya, etc.
  - Tier 3 (×1.2) : Éthiopie, Algérie, Espagne, Pologne
  - Tier 4 (×1.5) : Italie, Allemagne, Égypte
  - Tier 5 (×2.0) : France, Grande-Bretagne

---

## 10) Spéc SVG minimale (pour que le jeu fonctionne)
- 1 SVG par niveau/continent
- Doit avoir un `viewBox`
- Chaque pays/region = un path/polygon avec `id` stable:
  - `country-fr`, `country-dz`, etc.
  - `region-benelux` (pas de drapeau)
- Le jeu applique le `fill` selon owner (ne pas “baker” des couleurs définitives)
- Éviter les `transform` sur les paths si possible (simplifie tout)

---

## 11) MVP (plan de prod)
1. ✅ Prototype: 1 niveau (3–5 pays)
2. ✅ Units spawn + affichage compteur
3. ✅ Sélection source + ligne fantôme
4. ✅ Envoi all-but-1 + transferts + particules
5. ✅ Combat/capture + victoire/défaite
6. ✅ IA multi (jusqu'à 4 IA indépendantes)
7. ✅ Campagne 8 niveaux (Europe + Afrique)
8. ✅ Équilibrage réaliste (population + tier militaire)
9. ✅ Éditeur de niveaux complet (editeur.html)
10. ✅ Système de grades (S/A/B/C) + bestTime
11. ✅ Formations de troupes dynamiques

---

## 12) Éditeur de niveaux (editeur.html)
- Sidebar avec tous les paramètres de niveau et de pays
- **Dropdown flag searchable** : champ texte avec filtre insensible aux accents (~150 pays)
- **Config IA par IA** : sélecteur IA 1/2/3/4 avec preset et paramètres indépendants
- **Camp** : dropdown avec emojis couleur (🔵 Joueur, 🟥 IA 1, etc.)
- Génération de code `levels.js` prêt à coller
- Aperçu canvas en temps réel

---

## 13) Glossaire
- **Pays**: zone de carte conquérable, avec owner + unités + spawn
- **Node**: rond central (drapeau/icône + compteur)
- **Transfert**: envoi d'unités d'un pays vers un autre
- **PopulationTier**: tier (1..5) déterminant la vitesse de spawn, basé sur la puissance militaire réelle
- **Formation**: disposition des troupes en rangées lors de l'envoi (file indienne ou 2–4 rangées)
- **Grade**: S/A/B/C attribué selon le temps de victoire

---

## 14) Journal des changements récents

### 2026-03-29
- Ajout d'un **écran de fin enrichi** avec statistiques de manche:
  - pays le plus attaqué / le moins attaqué
  - pays le plus puissant
  - plus grosse armée
  - joueur le plus attaquant / le plus défensif
  - forteresse du niveau
  - maître des conquêtes
- Refonte **arcade** du panneau de fin avec cartes visuelles, badges et hiérarchie graphique plus marquée.
- Sauvegarde d'un **historique récent par niveau** (victoire/défaite, temps, grade, stats marquantes) dans le système de sauvegarde principal.
- Affichage de cet historique dans l'écran de fin.
- Ajout de **médailles arcade persistantes** par niveau:
  - Blitz
  - Dominateur
  - Mur de fer
  - Conquérant
- Enrichissement de la **grille de sélection des niveaux**:
  - meilleur grade
  - meilleur temps
  - dernier run
  - médailles gagnées
  - tooltip détaillé

### 2026-03-30
- Ajout d'une **transition d'entrée en niveau** de type rideau qui s'ouvre avec le **titre du niveau** affiché en grand au centre.
- Déclenchement de cette transition:
  - au lancement d'un niveau depuis la grille
  - au passage au niveau suivant depuis l'écran de victoire
- Ajout d'un **effet sonore synthétique** type "candy blop" à l'arrivée d'une troupe dans un camp adverse.
- Randomisation légère du blop:
  - forme d'onde
  - pitch
  - filtre
  - durée
  - enveloppe
- Ajout d'une **option dédiée Effets sonores** dans les paramètres, séparée de la musique.
- Ajout d'une **brillance animée transparente** sur les surfaces des pays pour éviter un remplissage figé.
- Différenciation visuelle des surfaces:
  - pays du joueur plus lumineux
  - pays neutres plus mats
  - pays IA intermédiaires
- Ajout d'un **effet de vague discret sur les frontières** des pays.
- Ajustement de la **durée de la transition rideau** et synchronisation du fondu noir pour qu'il disparaisse en même temps que l'ouverture.
- Ajout d'un **réglage de volume de la musique** dans les options, avec valeur par défaut à **50%**.
- Remplacement du toggle SFX par un **slider de volume des bruitages** persistant.
- Simplification visuelle des **cartes de sélection de niveau** pour réduire la surcharge de labels dans la carte.
- Ajout d'un **bandeau HUD live** plus compact affichant des leaders de partie en rotation:
  - plus grande armée
  - pays le plus puissant
  - joueur le plus offensif
  - forteresse
  - conquérant en cours
- Correction et extension des **traductions** de l'écran de fin, des statistiques, des médailles et de plusieurs labels d'interface selon la langue de l'URL.
- Ajout en bas de l'écran de sélection d'un **guide des médailles** expliquant les conditions de déblocage.
- Transformation de ce guide en **panneau repliable** avec mémorisation de l'état ouvert/fermé dans le navigateur.
- Mise à jour du branding UI:
  - titre principal affiché en `Nation Wars`
  - sous-titre modifié en `Conquérez le monde, pays par pays !`