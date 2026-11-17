"""Prototype décor — Terrain de football de quartier (BLOCKOUT).

Volumes gris de mise en place : échelle, géographie du terrain, emplacement
des immeubles, cages, grillage et spectateurs. Ce n'est PAS un décor final.

Produit :
- production/assets/decors/SET_terrain/SET_terrain_BLK_vNNN.blend
- production/rendus_tests/SET_terrain/SET_terrain_BLK_vNNN_present.png
- production/rendus_tests/SET_terrain/SET_terrain_BLK_vNNN_souvenir.png

Lancement (depuis la racine du dépôt) :
    blender -b -P scripts/blender/proto_decor_terrain.py -- --res 50 --samples 32
ou, avec le module bpy installé :
    python scripts/blender/proto_decor_terrain.py --res 50 --samples 32
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import rlo_commun as rc  # noqa: E402

# Dimensions provisoires d'un terrain de quartier (type city-stade agrandi).
LONGUEUR, LARGEUR = 40.0, 22.0
HAUT_GRILLAGE = 4.0


def cube(nom, taille, position, mat, col):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    o = bpy.context.object
    o.name = nom
    o.scale = taille
    o.data.materials.append(mat)
    rc.lier(o, col)
    return o


def construire_sol(col, m):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    sol = bpy.context.object
    sol.name = "SET_terrain_sol"
    sol.scale = (LONGUEUR + 4, LARGEUR + 4, 1)
    sol.data.materials.append(m["gazon"])
    rc.lier(sol, col)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.02))
    abords = bpy.context.object
    abords.name = "SET_terrain_abords"
    abords.scale = (160, 120, 1)
    abords.data.materials.append(m["bitume"])
    rc.lier(abords, col)

    # Lignes : contour, ligne médiane, rond central (approximé), surfaces.
    e = 0.08
    lignes = [
        ((LONGUEUR, e, .01), (0, LARGEUR / 2, .005)),
        ((LONGUEUR, e, .01), (0, -LARGEUR / 2, .005)),
        ((e, LARGEUR, .01), (LONGUEUR / 2, 0, .005)),
        ((e, LARGEUR, .01), (-LONGUEUR / 2, 0, .005)),
        ((e, LARGEUR, .01), (0, 0, .005)),
    ]
    for sx in (-1, 1):
        x = sx * (LONGUEUR / 2 - 6)
        lignes += [((e, 12, .01), (x, 0, .005)),
                   ((6, e, .01), (sx * (LONGUEUR / 2 - 3), 6, .005)),
                   ((6, e, .01), (sx * (LONGUEUR / 2 - 3), -6, .005))]
    for i, (t, p) in enumerate(lignes):
        cube(f"SET_terrain_ligne_{i:02d}", t, p, m["ligne"], col)
    bpy.ops.mesh.primitive_torus_add(major_radius=4, minor_radius=0.04, location=(0, 0, 0.005))
    rond = bpy.context.object
    rond.name = "SET_terrain_rond_central"
    rond.scale.z = 0.1
    rond.data.materials.append(m["ligne"])
    rc.lier(rond, col)


def construire_cages(col, m):
    for sx in (-1, 1):
        x = sx * LONGUEUR / 2
        for sy in (-1, 1):
            cube(f"PRP_cage_poteau_{'G' if sx < 0 else 'D'}{'a' if sy < 0 else 'b'}",
                 (.1, .1, 2.0), (x, sy * 2.5, 1.0), m["metal_blanc"], col)
        cube(f"PRP_cage_barre_{'G' if sx < 0 else 'D'}", (.1, 5.1, .1), (x, 0, 2.0), m["metal_blanc"], col)
        cube(f"PRP_cage_filet_{'G' if sx < 0 else 'D'}", (.02, 5.0, 1.95),
             (x + sx * 1.0, 0, 1.0), m["filet"], col)


def construire_grillage(col, m):
    # Panneaux semi-transparents + poteaux tous les 3 m.
    demi_l, demi_w = LONGUEUR / 2 + 2, LARGEUR / 2 + 2
    cotes = [((2 * demi_l, .03, HAUT_GRILLAGE), (0, demi_w, HAUT_GRILLAGE / 2)),
             ((2 * demi_l, .03, HAUT_GRILLAGE), (0, -demi_w, HAUT_GRILLAGE / 2)),
             ((.03, 2 * demi_w, HAUT_GRILLAGE), (demi_l, 0, HAUT_GRILLAGE / 2)),
             ((.03, 2 * demi_w, HAUT_GRILLAGE), (-demi_l, 0, HAUT_GRILLAGE / 2))]
    for i, (t, p) in enumerate(cotes):
        # Ouverture côté spectateurs (y négatif) : grillage plus bas.
        if i == 1:
            t = (t[0], t[1], 1.2)
            p = (p[0], p[1], 0.6)
        cube(f"SET_grillage_panneau_{i}", t, p, m["grillage"], col)
    x = -demi_l
    while x <= demi_l + 0.01:
        for y in (demi_w, -demi_w):
            h = 1.2 if y < 0 else HAUT_GRILLAGE
            cube("SET_grillage_poteau", (.06, .06, h), (x, y, h / 2), m["metal_vert"], col)
        x += 3.0


def construire_immeubles(col, m):
    """Barres et tours d'habitation en volumes simples, avec trame de fenêtres."""
    random.seed(7)
    implantations = [  # (centre x, centre y, longueur, profondeur, étages, rotation z)
        (-10, 42, 46, 12, 9, 0),
        (38, 30, 12, 30, 12, 0),
        (-46, 18, 12, 34, 7, 0),
        (22, -46, 40, 12, 6, 0),
        (-30, -44, 14, 14, 14, 0),
    ]
    teintes = ["creme", "terre_cuite_clair", "ocre_clair"]
    for i, (cx, cy, lx, ly, etages, rz) in enumerate(implantations):
        h = etages * 2.9
        corps = cube(f"SET_immeuble_{i:02d}", (lx, ly, h), (cx, cy, h / 2),
                     m[teintes[i % len(teintes)]], col)
        corps.rotation_euler.z = math.radians(rz)
        # Trame de fenêtres sur la façade orientée vers le terrain.
        face_y = cy - math.copysign(ly / 2 + 0.05, cy)
        nb_x = int(lx // 3.2)
        for e_ in range(etages):
            for k in range(nb_x):
                if random.random() < 0.06:
                    continue
                x = cx - lx / 2 + 1.6 + k * 3.2
                cube("SET_fenetre", (1.3, .1, 1.5), (x, face_y, 1.6 + e_ * 2.9),
                     m["vitre"], col)


def construire_vie(col, m):
    """Arbres, bancs, lampadaires et silhouettes de spectateurs (proxys)."""
    random.seed(3)
    for i, (x, y) in enumerate([(-30, -17), (30, -17), (-30, 2), (30, 4),
                                (-30, 20), (30, 20), (-12, 26), (14, 27)]):
        cube(f"PRP_arbre_tronc_{i:02d}", (.35, .35, 3.2), (x, y, 1.6), m["bois"], col)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=2.6 + random.random(),
                                              location=(x, y, 4.6 + random.random()))
        h = bpy.context.object
        h.name = f"PRP_arbre_houppier_{i:02d}"
        h.data.materials.append(m["feuillage"])
        rc.lier(h, col)
    for i, x in enumerate((-12, 0, 12)):
        cube(f"PRP_banc_{i:02d}", (2.2, .5, .45), (x, -LARGEUR / 2 - 4.2, .45), m["bois"], col)
    for i, x in enumerate((-22, 22)):
        cube(f"PRP_lampadaire_{i:02d}", (.15, .15, 7), (x, -LARGEUR / 2 - 3, 3.5), m["metal_vert"], col)
    # Parents / spectateurs : capsules neutres (personnages secondaires non conçus).
    for i in range(9):
        x = -14 + i * 3.4 + random.uniform(-.6, .6)
        hauteur = random.uniform(1.55, 1.85)
        bpy.ops.mesh.primitive_cylinder_add(radius=.22, depth=hauteur - .4,
                                            location=(x, -LARGEUR / 2 - 3.2, (hauteur - .4) / 2))
        c = bpy.context.object
        c.name = f"CHR_spectateur_proxy_{i:02d}"
        c.data.materials.append(m[random.choice(["vet_a", "vet_b", "vet_c"])])
        rc.lier(c, col)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.13, location=(x, -LARGEUR / 2 - 3.2, hauteur - .2))
        t = bpy.context.object
        t.name = f"CHR_spectateur_proxy_tete_{i:02d}"
        t.data.materials.append(m["peau"])
        rc.lier(t, col)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.11, location=(3, -2, .11))
    b = bpy.context.object
    b.name = "PRP_ballon"
    b.data.materials.append(m["ligne"])
    rc.lier(b, col)


def camera(col):
    """Plan d'ensemble depuis le bord spectateurs : géographie lisible."""
    cam_data = bpy.data.cameras.new("CAM_terrain_ensemble")
    cam_data.lens = 24
    cam = bpy.data.objects.new("CAM_terrain_ensemble", cam_data)
    col.objects.link(cam)
    cam.location = Vector((-4, -31, 8.5))
    direction = Vector((1, 6, 0)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam


AMBIANCES = {
    # Présent : lumière naturelle, palette plus sobre (BIBLE_GRAPHIQUE.md).
    "present": dict(soleil_couleur="#F2EEE6", soleil_force=3.2, elevation=48, azimut=140,
                    ciel="#9FB3C8", ciel_force=0.9),
    # Souvenir football : lumière dorée, couleurs plus vives.
    "souvenir": dict(soleil_couleur="#FFB063", soleil_force=5.5, elevation=16, azimut=120,
                     ciel="#E9B27A", ciel_force=1.1),
}


def eclairage(nom, col):
    a = AMBIANCES[nom]
    for o in [o for o in col.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(o)
    ld = bpy.data.lights.new(f"LGT_soleil_{nom}", "SUN")
    ld.energy = a["soleil_force"]
    ld.color = rc.hex_lineaire(a["soleil_couleur"])[:3]
    ld.angle = math.radians(2.0)
    lo = bpy.data.objects.new(f"LGT_soleil_{nom}", ld)
    col.objects.link(lo)
    lo.rotation_euler = (math.radians(90 - a["elevation"]), 0, math.radians(a["azimut"]))
    rc.monde_couleur(a["ciel"], a["ciel_force"])


def main():
    args = rc.arguments(__doc__.splitlines()[0])
    scene = rc.scene_vide()
    rc.reglages_rendu_test(scene, args.res, args.samples)

    m = {
        "gazon": rc.materiau("MAT_gazon_synth", rc.PALETTE["vert_doux"], .9),
        "bitume": rc.materiau("MAT_bitume", "#6E6A66", .95),
        "ligne": rc.materiau("MAT_ligne_blanche", "#EDEBE6", .7),
        "metal_blanc": rc.materiau("MAT_metal_blanc", "#E6E6E6", .35),
        "metal_vert": rc.materiau("MAT_metal_vert", "#3E5A48", .45),
        "filet": rc.materiau("MAT_filet_proxy", "#D8D8D8", .8),
        "grillage": rc.materiau("MAT_grillage_proxy", "#4D6656", .5),
        "creme": rc.materiau("MAT_facade_creme", rc.PALETTE["creme"], .85),
        "terre_cuite_clair": rc.materiau("MAT_facade_terre_cuite", "#D29A78", .85),
        "ocre_clair": rc.materiau("MAT_facade_ocre", "#E2BE84", .85),
        "vitre": rc.materiau("MAT_vitre_proxy", rc.PALETTE["bleu_nuit"], .2),
        "bois": rc.materiau("MAT_bois", "#6B4A33", .8),
        "feuillage": rc.materiau("MAT_feuillage", "#5E7A45", .9),
        "peau": rc.materiau("MAT_peau_proxy", "#7A4B33", .55, sss=.15),
        "vet_a": rc.materiau("MAT_vet_proxy_a", rc.PALETTE["bleu_nuit"], .8),
        "vet_b": rc.materiau("MAT_vet_proxy_b", rc.PALETTE["terre_cuite"], .8),
        "vet_c": rc.materiau("MAT_vet_proxy_c", rc.PALETTE["ocre"], .8),
    }
    # Grillage/filet : transparence partielle en attendant de vrais maillages.
    for cle in ("grillage", "filet"):
        b = m[cle].node_tree.nodes["Principled BSDF"]
        b.inputs["Alpha"].default_value = 0.25

    racine = rc.collection("SET_terrain")
    col_sol = rc.collection("SET_terrain_sol", racine)
    col_struct = rc.collection("SET_terrain_structures", racine)
    col_vie = rc.collection("SET_terrain_vie_proxy", racine)
    col_cam = rc.collection("CAM_LGT", racine)

    construire_sol(col_sol, m)
    construire_cages(col_struct, m)
    construire_grillage(col_struct, m)
    construire_immeubles(col_struct, m)
    construire_vie(col_vie, m)
    camera(col_cam)

    v = f"v{args.version:03d}"
    base = f"SET_terrain_BLK_{v}"
    durees = {}
    for nom in ("present", "souvenir"):
        eclairage(nom, col_cam)
        if not args.no_render:
            durees[nom] = rc.rendre(scene, rc.RENDUS_TESTS / "SET_terrain" / f"{base}_{nom}.png")
    eclairage("present", col_cam)
    rc.sauver_blend(rc.ASSETS / "decors" / "SET_terrain" / f"{base}.blend")
    print("[BILAN]", {k: round(d, 1) for k, d in durees.items()})


if __name__ == "__main__":
    main()
