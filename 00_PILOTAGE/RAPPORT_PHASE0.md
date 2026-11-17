# Rapport Phase 0 — Audit, architecture, prototypes

**Date :** 17/11/2026 · **Auteur :** Claude Code (responsable technique) · **Statut : en attente de validation du directeur artistique**

## 1. Ce qui a été fait

| Livrable | Fichier |
|---|---|
| Import du dossier de référence (aucun fichier modifié) | racine du dépôt |
| Audit du poste (exécuté réellement) | `00_PILOTAGE/audits/audit_conteneur_cloud_20261117.md` |
| Script d'audit réutilisable sur ton poste | `scripts/audit_poste.py` |
| Arborescence + conventions de nommage (proposition) | `06_PIPELINE_BLENDER/CONVENTIONS_ET_ARBORESCENCE.md` |
| Registre des assets (35 entrées) | `07_VALIDATION_PRODUCTION/REGISTRE_ASSETS.csv` |
| Liste des plans provisoire (14 plans, 4 320 images à 24 i/s) | `04_SCENARIO_STORYBOARD/LISTE_PLANS_PROVISOIRE.csv` |
| Prototype décor : blockout du terrain, éclairages présent/souvenir | `scripts/blender/proto_decor_terrain.py` |
| Prototype personnage : proxy de proportions adulte/ado | `scripts/blender/proto_personnage_proxy.py` |
| Questions bloquantes | `00_PILOTAGE/QUESTIONS_DIRECTEUR_ARTISTIQUE.md` |

## 2. Audit — machine actuelle

J'ai travaillé dans un **conteneur cloud temporaire**, pas sur ton ordinateur :

- Linux x86_64, 4 cœurs logiques, 15,7 Go de RAM, **aucun GPU**, environ 30 Go libres ;
- Blender disponible uniquement comme module Python `bpy` 5.3.0, installé pour ce test (pas d'interface graphique) ;
- **Cycles (CPU) fonctionne. EEVEE ne fonctionne pas ici** (pas de GPU ni d'OpenGL/Vulkan) ;
- FFmpeg, Git et Git LFS sont présents. DaVinci Resolve, REAPER et Krita sont absents.

**Conséquence :** ce conteneur suffit pour écrire et tester les scripts, faire les blockouts, les rendus de test et l'assemblage de l'animatique. **Il ne convient pas à la production finale.** L'audit de ta machine de production reste à faire : lance `python scripts/audit_poste.py` sur ton ordinateur et envoie-moi le rapport généré.

## 3. Coût de rendu — mesures réelles et extrapolation

Mesures réelles (Cycles CPU, 4 cœurs, 960×540, 32 échantillons + débruitage) :

| Image test | Durée mesurée |
|---|---|
| Blockout terrain — présent | 12,1 s |
| Blockout terrain — souvenir | 11,4 s |
| Proxy personnages (6 mannequins) | 13,4 s |

**Extrapolation (non mesurée, à vérifier) :** en 1920×1080, avec de vrais personnages (peau en SSS, cheveux, tissus), de la végétation et 128 échantillons ou plus, il faut compter plusieurs minutes par image sur ce type de CPU. Pour 4 320 images, cela représente **des centaines d'heures de rendu**. Sur le CPU de ce conteneur, un rendu final n'est donc pas réaliste. Les options sont un GPU (Cycles avec OptiX/HIP/Metal, ou EEVEE), un rendu par couches ou une ferme de rendu. Le choix se fera après un test sur ta machine.

## 4. Prototypes — ce qu'ils sont et ce qu'ils ne sont pas

Ce sont des **volumes de mise en place**, pas des modèles finaux.

- **Terrain** (`production/rendus_tests/SET_terrain/`) : géographie lisible (terrain d'environ 40 × 22 m, deux cages, grillage, bord spectateurs, barres d'immeubles), une caméra de plan d'ensemble, deux ambiances (présent sobre / souvenir doré). Il sert à valider l'échelle, l'implantation et la logique de lumière. Il ne dit rien du style final.
- **Personnage** (`production/rendus_tests/CHR_amadou/`) : mannequins adulte (1,78 m) et ado (1,70 m) en vues face, trois-quarts et profil, avec repères de hauteur. Ils servent à valider le gabarit, la silhouette et le code couleur des costumes. **Ils n'ont pas de visage**, car l'identité faciale est le vrai test de continuité, à faire en sculpture.

## 5. Limite importante à décider

La qualité visée (« 3D de long métrage », visages très expressifs, cheveux crépus, tissus) **ne peut pas être obtenue uniquement par des scripts Python.** Je peux automatiser et construire :

- l'arborescence, les liens entre assets et les conventions ;
- les blockouts et les décors modulaires (immeubles, mobilier, grillages, terrain) ;
- le layout, les caméras, les éclairages et les réglages de rendu ;
- l'animatique, les rendus par lots et l'assemblage FFmpeg ;
- les vérifications automatiques (nommage, chemins, durées).

En revanche, la **sculpture des visages, la topologie faciale, le rig facial et l'animation d'acting** demandent un travail artistique à la main dans Blender : le tien, celui d'un ou d'une artiste 3D, ou une base de départ libre de droits (par exemple MPFB, extension Blender dont les sorties sont sous licence CC0) que l'on stylise ensuite. C'est la décision qui conditionne le plus le planning (voir questions).

## 6. Plan technique proposé

1. **Moteur :** Cycles pour la qualité de référence, EEVEE à évaluer sur ton GPU pour la vitesse. Décision après une image test par décor sur ta machine.
2. **Fichiers :** une bibliothèque d'assets liée (`production/assets/`) et un fichier `.blend` par plan (`production/sequences/SQxxx/SHxxx/`).
3. **Personnages :** une base faciale unique, déclinée en deux âges (formes de visage ou modèle dérivé). Corps riggé avec Rigify, rig facial à définir selon la base retenue.
4. **Éclairage :** deux familles de lumière, présent et souvenir, décrites en script (le prototype en contient déjà une première version), plus une ambiance intérieure pour la maison.
5. **Animatique :** vignettes de storyboard minutées d'après la liste des plans, montées avec FFmpeg (ou Resolve si tu l'utilises), voix temporaires et maquette musicale.
6. **Son :** un motif original de 5 à 8 notes. Je peux proposer des maquettes MIDI. La composition finale est à confier (à décider).

## 7. Planning indicatif

Estimation pour une petite équipe (toi plus Claude Code, avec de l'aide ponctuelle pour la sculpture et le son). À revoir après tes réponses.

| Phase | Durée indicative | Validation |
|---|---|---|
| 0 — Audit et architecture | fait (sauf audit de ta machine) | architecture et faisabilité |
| 1 — Préproduction (noms, dialogues, métier, storyboard, maquette musicale) | 2–4 semaines | bible et storyboard |
| 2 — Prototypes (Amadou deux âges, mère, salon, terrain, test de lumière) | 4–8 semaines | qualité visuelle |
| 3 — Animatique 3 min | 2–3 semaines | rythme et compréhension |
| 4 — Production (modèles, rigs, animation de 14 plans, éclairage, rendu) | 3–6 mois | séquences de test |
| 5 — Finition (montage, son, mixage, étalonnage, carton final) | 3–6 semaines | export final |

## 8. Prochaine étape proposée (après ta validation)

1. Tu réponds aux questions bloquantes.
2. Tu lances `scripts/audit_poste.py` sur ta machine.
3. Je produis le blockout du **salon et de la cuisine**, et je prépare les vignettes de l'**animatique** sur la base de la liste des plans.
4. Pour les personnages, selon ta décision sur la sculpture : soit je prépare la base de travail et ses scripts (proportions, Rigify, matériaux), soit j'intègre les modèles fournis.
