"""Utilitaires communs — Le rêve oublié.

Module partagé par les scripts Blender du projet. Tous les chemins sont
calculés relativement à la racine du dépôt (jamais de chemin absolu propre
à une machine).

Fonctionne avec le binaire Blender (`blender -b -P script.py -- ...`) comme
avec le module Python `bpy` (`python script.py ...`).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import bpy

# --- Chemins ---------------------------------------------------------------
RACINE = Path(__file__).resolve().parents[2]
PRODUCTION = RACINE / "production"
ASSETS = PRODUCTION / "assets"
RENDUS_TESTS = PRODUCTION / "rendus_tests"

# --- Palette de référence (BIBLE_GRAPHIQUE.md, indicative) ------------------
PALETTE = {
    "bordeaux": "#7F1F2D",
    "ocre": "#D99A32",
    "bleu_nuit": "#243B5A",
    "vert_doux": "#81966B",
    "creme": "#E8D7B8",
    "terre_cuite": "#B96B45",
}


def hex_lineaire(hex_str: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    """Convertit une couleur sRGB hexadécimale en RGBA linéaire (pour Blender)."""
    h = hex_str.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, alpha)


def arguments(description: str) -> argparse.Namespace:
    """Arguments communs. Avec le binaire Blender, ils se placent après `--`."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--res", type=int, default=50,
                   help="Pourcentage de 1920x1080 (défaut 50 = 960x540).")
    p.add_argument("--samples", type=int, default=32, help="Échantillons Cycles.")
    p.add_argument("--no-render", action="store_true", help="Construit la scène sans rendre.")
    p.add_argument("--version", type=int, default=1, help="Numéro de version (vNNN).")
    return p.parse_args(argv)


def scene_vide() -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = 24
    return scene


def reglages_rendu_test(scene: bpy.types.Scene, res_pct: int, samples: int) -> None:
    """Rendu de test : Cycles CPU, 16:9, basse résolution, débruitage."""
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = res_pct
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"


def materiau(nom: str, couleur: str, rugosite: float = 0.6, sss: float = 0.0):
    mat = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = hex_lineaire(couleur)
    bsdf.inputs["Roughness"].default_value = rugosite
    if sss:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        bsdf.inputs["Subsurface Scale"].default_value = 0.01
    mat.diffuse_color = hex_lineaire(couleur)
    return mat


def collection(nom: str, parent=None) -> bpy.types.Collection:
    col = bpy.data.collections.new(nom)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def lier(obj, col) -> None:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def monde_couleur(couleur: str, force: float = 1.0) -> None:
    world = bpy.data.worlds.new("WLD_test")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hex_lineaire(couleur)
    bg.inputs["Strength"].default_value = force


def rendre(scene, chemin: Path) -> float:
    """Rend l'image courante et renvoie la durée réelle en secondes."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(chemin)
    t0 = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    duree = time.perf_counter() - t0
    print(f"[RENDU] {chemin.relative_to(RACINE)} — {duree:.1f} s")
    return duree


def sauver_blend(chemin: Path) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(chemin), relative_remap=True, compress=True)
    print(f"[BLEND] {chemin.relative_to(RACINE)}")
