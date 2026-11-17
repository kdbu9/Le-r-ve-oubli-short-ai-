# Pipeline technique — Blender et outils annexes

## Principe
Claude Code peut écrire des scripts, organiser les fichiers et piloter des opérations automatisables. Blender réalise la création et le rendu 3D. Ne pas prétendre qu'un agent de code remplace à lui seul le travail artistique, les validations ou les ajustements manuels.

## Audit initial
Avant de choisir une méthode :
- relever le système d'exploitation ;
- vérifier Blender et sa version ;
- vérifier CPU, GPU, mémoire vive et espace disque ;
- vérifier les logiciels audio et montage disponibles ;
- estimer le coût de rendu d'une image test.

## Pipeline conseillé
1. Préproduction : scénario, bible, concept arts, storyboard.
2. Animatique : images temporaires, voix de travail, timing et montage.
3. Modélisation : personnages et décors modulaires.
4. Matériaux : peau, cheveux, tissus, surfaces et accessoires.
5. Rigging : squelette, contrôleurs, rig facial et tests.
6. Layout : caméras, échelle et positions.
7. Animation : blocking, spline, polish.
8. Éclairage : configurations cohérentes présent/passé.
9. Rendu : tests basse résolution puis rendu final.
10. Postproduction : montage, colorimétrie, musique, bruitages, mixage et export.

## Organisation Blender
- Une scène ou un fichier par séquence lorsque cela facilite la gestion.
- Assets liés ou appendés depuis une bibliothèque centrale.
- Personnages et accessoires réutilisables.
- Conventions de nommage explicites.
- Sauvegardes versionnées.
- Scripts Python conservés dans le dossier de projet.

## Performances
- Ne pas supposer que le matériel peut rendre 4 320 images en haute qualité.
- Tester une image représentative de chaque environnement.
- Utiliser proxy, basse résolution, denoising et rendu par couches si pertinent.
- Choisir le moteur de rendu après tests.
- Conserver les fichiers source et les paramètres de rendu.

## Outils possibles
- Blender : 3D.
- Python : automatisation.
- DaVinci Resolve : montage, étalonnage et finition.
- REAPER : musique, dialogues et mixage.
- Krita : storyboard et concepts dessinés.

Ces outils sont des options ; vérifier leur disponibilité avant de les intégrer au pipeline.
