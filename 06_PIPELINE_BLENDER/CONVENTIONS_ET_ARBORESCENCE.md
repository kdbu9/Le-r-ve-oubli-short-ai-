# Conventions de nommage et arborescence — proposition v1

> **Statut : proposition à valider.** Rien n'est figé tant que le directeur artistique n'a pas validé la Phase 0.

## Arborescence

```
.
├── CLAUDE.md, README.md          # Dossier de référence (inchangé)
├── 00_PILOTAGE/                  # Brief, rapport Phase 0, questions, audits
├── 01_…07_/                      # Dossier de référence + documents de production ajoutés
├── scripts/
│   ├── audit_poste.py            # Audit matériel/logiciels (bibliothèque standard)
│   └── blender/
│       ├── rlo_commun.py         # Chemins relatifs, palette, réglages de rendu test
│       ├── proto_decor_terrain.py
│       └── proto_personnage_proxy.py
└── production/
    ├── assets/
    │   ├── personnages/CHR_<nom>/     # Un dossier par personnage
    │   ├── decors/SET_<nom>/
    │   └── accessoires/PRP_<nom>/
    ├── sequences/SQ010/SH010/         # Fichiers de plan (layout, anim, éclairage)
    ├── rendus_tests/                  # Rendus basse résolution versionnés (suivis par git)
    ├── rendus/                        # Rendus lourds (IGNORÉS par git)
    ├── audio/                         # MUS_, SFX_, DIA_
    └── montage/                       # Animatique, montage, exports
```

## Préfixes

| Préfixe | Type | Exemple |
|---|---|---|
| `CHR_` | Personnage | `CHR_amadouAdulte` |
| `SET_` | Décor | `SET_terrain` |
| `PRP_` | Accessoire | `PRP_ballon` |
| `MAT_` | Matériau | `MAT_peau_amadou` |
| `CAM_` / `LGT_` | Caméra / lumière | `CAM_SQ020_SH020`, `LGT_soleil_souvenir` |
| `MUS_` / `SFX_` / `DIA_` | Musique / bruitage / dialogue | `SFX_ballon_rebond_01` |

## Étapes (suffixe de tâche)

`BLK` blockout · `PRX` proxy · `MOD` modélisation · `SCL` sculpture · `TEX` textures/matériaux · `RIG` rig · `LAY` layout · `ANM` animation · `LGT` éclairage · `RND` rendu · `CMP` compositing · `EDT` montage

## Format des noms de fichiers

```
<ASSET>_<ETAPE>_v<NNN>.blend            CHR_amadouAdo_MOD_v003.blend
<SQ>_<SH>_<ETAPE>_v<NNN>.blend          SQ020_SH020_ANM_v012.blend
<SQ>_<SH>_<ETAPE>_v<NNN>.<####>.exr     SQ020_SH020_RND_v004.0961.exr
```

- Versions sur 3 chiffres, jamais écrasées : on crée `v002` au lieu de modifier `v001`.
- Les numéros d'images suivent la liste des plans (`04_SCENARIO_STORYBOARD/LISTE_PLANS_PROVISOIRE.csv`), où la numérotation commence à 1 sur l'ensemble du film.
- Pas d'espaces, pas d'accents dans les noms de fichiers ; camelCase pour le nom d'asset.

## Liens entre fichiers

- Les personnages, décors et accessoires sont **liés** (`Link`) dans les fichiers de plan depuis `production/assets/`. Ils ne sont appendés que pour une exception locale documentée.
- Les chemins sont toujours relatifs (`//…`) : les scripts appellent `save_as_mainfile(relative_remap=True)`.

## Stockage

- Les rendus lourds (`production/rendus/`), les caches et les `*.blend1` sont ignorés par git.
- Recommandation pour les binaires lourds (`.blend`, textures, `.wav`) : **Git LFS** (à valider, voir questions).
