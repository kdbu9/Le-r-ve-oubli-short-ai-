# Scripts — Le rêve oublié

Tous les scripts se lancent **depuis la racine du dépôt**. Ils n'utilisent que des chemins relatifs.

## Audit du poste
```bash
python scripts/audit_poste.py
```
Écrit `00_PILOTAGE/audits/audit_<machine>_<date>.md`. Bibliothèque standard uniquement.

## Prototypes Blender
Avec Blender installé (version 4.2 LTS ou plus récente recommandée ; testé avec `bpy` 5.3.0) :
```bash
blender -b -P scripts/blender/proto_decor_terrain.py -- --res 50 --samples 32
blender -b -P scripts/blender/proto_personnage_proxy.py -- --res 50 --samples 32
```
Sans interface, avec le module Python `bpy` (`pip install bpy`, avec la version de Python exigée par bpy) :
```bash
python scripts/blender/proto_decor_terrain.py --res 50
```

| Option | Effet |
|---|---|
| `--res N` | Pourcentage de 1920×1080 (50 = 960×540) |
| `--samples N` | Échantillons Cycles |
| `--version N` | Écrit `..._v00N` (ne remplace pas les versions précédentes si N change) |
| `--no-render` | Construit et sauvegarde la scène sans rendre |

Sorties :
- scènes : `production/assets/...` ;
- images : `production/rendus_tests/...`.

Le rendu se fait en Cycles sur CPU par défaut, pour fonctionner partout. Le choix du GPU se fera après l'audit de la machine de production.
