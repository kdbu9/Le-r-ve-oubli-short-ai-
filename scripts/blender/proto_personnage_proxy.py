"""Prototype personnage — Amadou adulte / adolescent (PROXY DE PROPORTIONS).

Mannequins en primitives pour valider tailles, silhouettes et code couleur
des costumes AVANT toute sculpture. Ce n'est PAS un modèle de personnage :
pas de visage, pas de topologie d'animation, pas de rig.

Les tailles (1,78 m / 1,70 m) viennent de la planche générée 01 et sont
PROVISOIRES tant que le directeur artistique ne les a pas validées.

Produit :
- production/assets/personnages/CHR_amadou/CHR_amadou_PRX_vNNN.blend
- production/rendus_tests/CHR_amadou/CHR_amadou_PRX_vNNN_comparaison.png

Lancement (depuis la racine du dépôt) :
    blender -b -P scripts/blender/proto_personnage_proxy.py -- --res 50
ou :
    python scripts/blender/proto_personnage_proxy.py --res 50
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import rlo_commun as rc  # noqa: E402


@dataclass
class Gabarit:
    nom: str
    taille: float          # m
    tete: float            # hauteur de tête en fraction de la taille
    epaules: float         # demi-largeur d'épaules (m)
    torse_prof: float      # demi-profondeur du torse (m)
    ventre: float          # facteur d'épaisseur de la taille (1 = droit)
    membre: float          # rayon de base des membres (m)
    haut: str              # matériau haut
    bas: str               # matériau bas
    chaussures: str
    gilet: bool = False


ADULTE = Gabarit("CHR_amadouAdulte_PRX", 1.78, 1 / 7.0, .235, .14, 1.18, .062,
                 "haut_marine", "pantalon_sombre", "chaussure_travail", gilet=True)
ADO = Gabarit("CHR_amadouAdo_PRX", 1.70, 1 / 7.3, .205, .105, .95, .050,
              "maillot_bordeaux", "short_bordeaux", "crampon")


def prim(kind, nom, loc, scale, mat, col, rot=(0, 0, 0), **kw):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc, **kw)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, location=loc, **kw)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, **kw)
    o = bpy.context.object
    o.name = nom
    o.scale = scale
    o.rotation_euler = rot
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    rc.lier(o, col)
    return o


def mannequin(g: Gabarit, m, col, x_offset: float):
    """Construit un mannequin et le rattache à un vide racine positionné en x."""
    racine = bpy.data.objects.new(g.nom, None)
    col.objects.link(racine)
    H = g.taille
    th = H * g.tete
    parts = []
    # Repères verticaux (canon approximatif, à affiner en sculpture).
    z_cheville, z_genou, z_hanche = .07 * H, .285 * H, .52 * H
    z_taille, z_epaule = .62 * H, .815 * H
    z_cou = z_epaule + .02 * H

    # Tête + cou
    parts.append(prim("sphere", f"{g.nom}_tete", (0, 0, H - th / 2), (th * .40, th * .46, th / 2),
                      m["peau"], col))
    parts.append(prim("cyl", f"{g.nom}_cou", (0, 0, z_cou + .03), (g.membre * 1.05, g.membre * 1.05, .06),
                      m["peau"], col))
    # Cheveux courts crépus : calotte (proxy)
    parts.append(prim("sphere", f"{g.nom}_cheveux", (0, .005, H - th * .36),
                      (th * .43, th * .48, th * .36), m["cheveux"], col))
    # Torse (cage) + bassin
    torse_h = z_epaule - z_taille
    parts.append(prim("cyl", f"{g.nom}_torse", (0, 0, z_taille + torse_h / 2),
                      (g.epaules * .92, g.torse_prof, torse_h / 2), m[g.haut], col))
    parts.append(prim("sphere", f"{g.nom}_ventre", (0, -.01, z_taille + .02),
                      (g.epaules * .80 * g.ventre, g.torse_prof * g.ventre, .13), m[g.haut], col))
    parts.append(prim("cyl", f"{g.nom}_bassin", (0, 0, (z_taille + z_hanche) / 2 - .02),
                      (g.epaules * .78, g.torse_prof * .95, (z_taille - z_hanche) / 2 + .04), m[g.bas], col))
    if g.gilet:
        parts.append(prim("cyl", f"{g.nom}_gilet", (0, 0, z_taille + torse_h * .55),
                          (g.epaules * .97, g.torse_prof * 1.12, torse_h * .47), m["gilet_fluo"], col))
        for dz in (.33, .62):
            parts.append(prim("cyl", f"{g.nom}_bande_reflechissante", (0, 0, z_taille + torse_h * dz),
                              (g.epaules * .99, g.torse_prof * 1.15, .012), m["reflechissant"], col))
    # Bras (épaule -> poignet), légèrement écartés
    for s in (-1, 1):
        cote = "G" if s > 0 else "D"
        long_bras = z_epaule - z_hanche + .04
        parts.append(prim("sphere", f"{g.nom}_epaule_{cote}", (s * g.epaules, 0, z_epaule - .03),
                          (g.membre * 1.5,) * 3, m[g.haut], col))
        parts.append(prim("cyl", f"{g.nom}_bras_{cote}",
                          (s * (g.epaules + .03), 0, z_epaule - long_bras / 2 - .02),
                          (g.membre * 1.1, g.membre * 1.1, long_bras / 2), m[g.haut if g.gilet else "peau"],
                          col, rot=(0, s * math.radians(-4), 0)))
        if not g.gilet:  # manches courtes du maillot
            parts.append(prim("cyl", f"{g.nom}_manche_{cote}", (s * (g.epaules + .01), 0, z_epaule - .08),
                              (g.membre * 1.4, g.membre * 1.4, .09), m[g.haut], col))
        parts.append(prim("sphere", f"{g.nom}_main_{cote}",
                          (s * (g.epaules + .06), 0, z_epaule - long_bras - .06),
                          (g.membre * .9, g.membre * .6, g.membre * 1.5), m["peau"], col))
        # Jambes
        xl = s * g.epaules * .45
        parts.append(prim("cyl", f"{g.nom}_cuisse_{cote}", (xl, 0, (z_hanche + z_genou) / 2),
                          (g.membre * 1.7, g.membre * 1.7, (z_hanche - z_genou) / 2 + .02), m[g.bas], col))
        mollet_mat = m["chaussette_creme"] if not g.gilet else m[g.bas]
        if not g.gilet:  # short : cuisse visible sous le short
            parts[-1].scale.z *= .55
            parts[-1].location.z = z_hanche - (z_hanche - z_genou) * .3
            parts.append(prim("cyl", f"{g.nom}_cuisse_peau_{cote}", (xl, 0, (z_hanche + z_genou) / 2 - .05),
                              (g.membre * 1.45, g.membre * 1.45, (z_hanche - z_genou) / 2 - .04), m["peau"], col))
        parts.append(prim("cyl", f"{g.nom}_mollet_{cote}", (xl, 0, (z_genou + z_cheville) / 2),
                          (g.membre * 1.25, g.membre * 1.25, (z_genou - z_cheville) / 2 + .02), mollet_mat, col))
        parts.append(prim("cube", f"{g.nom}_pied_{cote}", (xl, -.04, z_cheville / 2),
                          (.10, .26, z_cheville), m[g.chaussures], col))
    for p in parts:
        p.parent = racine
    racine.location.x = x_offset
    return racine


def main():
    args = rc.arguments(__doc__.splitlines()[0])
    scene = rc.scene_vide()
    rc.reglages_rendu_test(scene, args.res, args.samples)
    m = {
        "peau": rc.materiau("MAT_peau_proxy", "#6E412B", .5, sss=.2),
        "cheveux": rc.materiau("MAT_cheveux_proxy", "#1B1411", .9),
        "haut_marine": rc.materiau("MAT_haut_marine", rc.PALETTE["bleu_nuit"], .8),
        "pantalon_sombre": rc.materiau("MAT_pantalon_sombre", "#2A3140", .85),
        "gilet_fluo": rc.materiau("MAT_gilet_fluo", "#D8E63A", .6),
        "reflechissant": rc.materiau("MAT_bande_reflechissante", "#C9CCCF", .25),
        "chaussure_travail": rc.materiau("MAT_chaussure_travail", "#2B2522", .6),
        "maillot_bordeaux": rc.materiau("MAT_maillot_bordeaux", rc.PALETTE["bordeaux"], .7),
        "short_bordeaux": rc.materiau("MAT_short_bordeaux", "#6C1A26", .7),
        "chaussette_creme": rc.materiau("MAT_chaussette_creme", rc.PALETTE["creme"], .8),
        "crampon": rc.materiau("MAT_crampon", "#1E1E1E", .5),
        "fond": rc.materiau("MAT_fond_studio", "#D9D4CC", .9),
        "repere": rc.materiau("MAT_repere", "#8A3B22", .7),
    }
    col = rc.collection("CHR_amadou_PRX")
    col_studio = rc.collection("STUDIO")

    # Trois vues (face, 3/4, profil) pour chaque âge : adulte à gauche, ado à droite.
    vues = [("face", 0), ("trois_quarts", -40), ("profil", -90)]
    x = -3.3
    for nom_vue, angle in vues:
        for g in (ADULTE, ADO):
            r = mannequin(g, m, col, x)
            r.name = f"{g.nom}_{nom_vue}"
            r.rotation_euler.z = math.radians(angle)
            x += .95
        x += .35

    # Fond studio (cyclo) + règles de hauteur 1,70 / 1,78 m
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 1.5, 0))
    sol = bpy.context.object
    sol.scale = (20, 12, 1)
    sol.data.materials.append(m["fond"])
    rc.lier(sol, col_studio)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 3, 3), rotation=(math.radians(90), 0, 0))
    mur = bpy.context.object
    mur.scale = (20, 6, 1)
    mur.data.materials.append(m["fond"])
    rc.lier(mur, col_studio)
    for h in (ADO.taille, ADULTE.taille):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 2.95, h))
        t = bpy.context.object
        t.name = f"REPERE_{int(h * 100)}cm"
        t.scale = (7.6, .01, .012)
        t.data.materials.append(m["repere"])
        rc.lier(t, col_studio)

    # Caméra orthographique (planche technique) + éclairage 3 points simple
    cd = bpy.data.cameras.new("CAM_planche")
    cd.type = "ORTHO"
    cd.ortho_scale = 6.4
    cam = bpy.data.objects.new("CAM_planche", cd)
    col_studio.objects.link(cam)
    # Caméra horizontale : les repères 1,70 / 1,78 m restent alignés sur les têtes.
    cam.location = (-.58, -10, 1.15)
    cam.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cam
    for nom, loc, e, c in [("cle", (-4, -5, 5), 900, "#FFE9D2"),
                           ("debouchage", (5, -6, 2.5), 300, "#DDE6F5"),
                           ("contre", (0, 2, 5), 450, "#FFFFFF")]:
        ld = bpy.data.lights.new(f"LGT_{nom}", "AREA")
        ld.energy = e
        ld.size = 3
        ld.color = rc.hex_lineaire(c)[:3]
        lo = bpy.data.objects.new(f"LGT_{nom}", ld)
        col_studio.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector((0, 0, 1)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    rc.monde_couleur("#BFC4CC", .4)

    v = f"v{args.version:03d}"
    if not args.no_render:
        d = rc.rendre(scene, rc.RENDUS_TESTS / "CHR_amadou" / f"CHR_amadou_PRX_{v}_comparaison.png")
        print("[BILAN]", round(d, 1))
    rc.sauver_blend(rc.ASSETS / "personnages" / "CHR_amadou" / f"CHR_amadou_PRX_{v}.blend")


if __name__ == "__main__":
    main()
