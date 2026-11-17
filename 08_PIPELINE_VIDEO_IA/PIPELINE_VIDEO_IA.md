# Pipeline vidéo IA — Le rêve oublié

> **Décision du directeur artistique (17/11/2026)** : le film est produit en génération vidéo par IA, dans le style « 3D stylisée de long métrage » des planches de référence. Le pipeline Blender (Phase 0) est mis en pause. Ses fichiers sont conservés : le blockout du terrain peut servir de référence de géographie.

## 1. Vue d'ensemble

```
Planches de référence ─► Fiches de référence propres (REFERENCES_IA/)
                              │
Bible des prompts ────────────┤
                              ▼
1. Images clés (1 par plan, plusieurs essais) ── validation DA ──┐
                                                                 ▼
2. Image clé → vidéo (4–10 s par plan) ── validation DA ──► production/ia/clips/
                                                                 │
3. Voix (dialogues) → synchronisation labiale (plans de dialogue)│
                                                                 ▼
4. Assemblage : scripts/ia/assembler_animatique.py ─► production/montage/
5. Musique originale, bruitages, mixage, étalonnage, carton final
```

## 2. Outils (catalogue Higgsfield de ton compte, vérifié le 17/11/2026)

| Étape | Outil conseillé | Pourquoi |
|---|---|---|
| Images clés | **Nano Banana Pro** (jusqu'à 14 images de référence) | Garde le mieux les visages quand on lui donne les fiches |
| Variante d'images | Seedream 4.5 / Cinema Studio Image 2.5 | Plans larges, décors, lumière cinéma |
| Image clé → vidéo | **Seedance 2.0 / 2.5** (std, 1080p) | Pensé pour la cohérence d'identité, accepte image de départ, image de fin et références |
| Plans d'émotion (gros plans) | Minimax Hailuo 2.3 | Expressions faciales et physique naturelles |
| Plans spectaculaires (match) | Cinema Studio Video 3.0 | Caméra et composition cinéma |
| Dialogues | Voix enregistrées ou synthétiques, puis **Sync Lipsync 3** | Synchronisation des lèvres sur la voix finale |
| Montage | `scripts/ia/assembler_animatique.py`, puis DaVinci Resolve ou CapCut | Assemblage reproductible, finition manuelle |

**Crédits :** le compte a **10 crédits** au 17/11/2026. Une génération vidéo en coûte beaucoup plus, selon le modèle, la durée et la résolution. Prévoir 35 plans avec 3 à 5 essais chacun, soit environ 100 à 175 générations vidéo, plus les images clés. Il faut recharger avant la production.

**Conseil coût :** générer d'abord en **480p ou 720p (mode « fast » ou brouillon)** pour valider le jeu et le mouvement, puis relancer en 1080p uniquement les prises retenues. Seedance 2.5 propose un mode brouillon finalisable.

## 3. Règles de cohérence

1. **Toujours** joindre les fiches `REFERENCES_IA/` du ou des personnages présents, et utiliser les blocs `PERSO_…` de la bible mot pour mot.
2. Valider **l'image clé avant la vidéo** : c'est 10 fois moins cher de corriger une image qu'une vidéo.
3. Quand un plan doit raccorder avec le suivant (même lieu, même action), utiliser la **dernière image du plan précédent** comme image de départ ou de référence.
4. Une seule action par plan. Les gestes complexes (dribbles) sont découpés en plusieurs plans courts.
5. Pas de texte généré à l'image. Le carton final est fabriqué par le script de montage, avec les textes verrouillés.
6. Garder **toutes** les prises : les nommer, ne jamais écraser une version.

## 4. Nommage et rangement

```
production/ia/
├── images_cles/   SQ020_SH020_C01_IMG_v003.png
├── clips/         SQ020_SH020_C01_v002.mp4      ← prise retenue (la plus haute version est utilisée)
├── rejets/        prises écartées (gardées pour mémoire)
└── voix/          DIA_MERE_01_v001.wav
```
Le suivi des prompts réellement utilisés se fait dans la colonne `statut` de `DECOUPAGE_PLANS_IA.csv` (ou dans un fichier `prompts_utilises.md`).

## 5. Animatique

```
python scripts/ia/assembler_animatique.py --version 2            # 1280×720, son coupé
python scripts/ia/assembler_animatique.py --version 3 --audio    # garde le son des clips
```
Les plans encore non générés apparaissent en vignettes de couleur, avec le minutage et l'action. La durée totale est vérifiée à 180 s.

## 6. Limites connues de la vidéo IA (à anticiper)

- **Dérive des visages** d'un plan à l'autre : on la limite par les références et la validation des images clés, et on refait les plans qui dérivent.
- **Mains, ballon et pieds** pendant les dribbles : prévoir plus d'essais pour la séquence 2.
- **Durée** : 4 à 15 s par génération, d'où le découpage en 35 plans.
- **Lèvres** : les dialogues demandent la synchronisation labiale en post-production.
- **Droits** : vérifier les conditions d'utilisation commerciale du compte Higgsfield, et des outils de musique si une IA est utilisée, avant diffusion ou festival.
