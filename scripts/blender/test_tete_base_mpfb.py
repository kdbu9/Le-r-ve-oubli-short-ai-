"""Test de rendu — Tête d'Amadou adulte / adolescent sur base MakeHuman (CC0).

TEST DE FAISABILITÉ, PAS UN PERSONNAGE FINAL. Il montre ce qu'on obtient en
partant d'une base humaine libre de droits, avant toute sculpture manuelle :
même maillage pour les deux âges (règle de continuité), peau en diffusion
sous-surfacique, yeux procéduraux, cheveux crépus et barbe en poils Cycles.

Données utilisées (lues comme DONNÉES, aucun code tiers n'est exécuté) :
- maillage de base `3dobjs/base.obj` et cibles `targets/**.target.gz`
  du projet MPFB/MakeHuman, publiés sous licence CC0 ;
- masques UV `textures/mpfb_lips.jpg` (lèvres).

Récupérer les données (non versionnées dans ce dépôt, ~100 Mo) :
    git clone --depth 1 https://github.com/makehumancommunity/mpfb2 externe/mpfb2

Lancement :
    blender -b -P scripts/blender/test_tete_base_mpfb.py -- --mpfb externe/mpfb2/src/mpfb/data
    python scripts/blender/test_tete_base_mpfb.py --mpfb externe/mpfb2/src/mpfb/data
"""
from __future__ import annotations

import argparse
import gzip
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import rlo_commun as rc  # noqa: E402

ECHELLE = 0.1  # unités MakeHuman (décimètres) -> mètres


# --------------------------------------------------------------------------
# Lecture des données MakeHuman
# --------------------------------------------------------------------------
def lire_obj(chemin: Path):
    verts, uvs, groupes = [], [], {}
    courant = None
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            if ligne.startswith("v "):
                verts.append([float(x) for x in ligne.split()[1:4]])
            elif ligne.startswith("vt "):
                uvs.append([float(x) for x in ligne.split()[1:3]])
            elif ligne.startswith("g "):
                courant = ligne.split()[1]
                groupes.setdefault(courant, [])
            elif ligne.startswith("f "):
                face = [tuple(int(i) - 1 for i in p.split("/")[:2]) for p in ligne.split()[1:]]
                groupes[courant].append(face)
    return np.array(verts, dtype=np.float64), np.array(uvs, dtype=np.float64), groupes


def lire_cible(chemin: Path, n: int) -> np.ndarray:
    delta = np.zeros((n, 3))
    with gzip.open(chemin, "rt", encoding="utf-8") as f:
        for ligne in f:
            if not ligne.strip() or ligne.startswith("#"):
                continue
            i, x, y, z = ligne.split()
            delta[int(i)] = (float(x), float(y), float(z))
    return delta


def poids_trois(v: float, noms=("min", "average", "max")) -> dict:
    """Valeur 0..1 -> poids des trois catégories (0,5 = moyenne)."""
    if v < 0.5:
        return {noms[0]: 1 - v / 0.5, noms[1]: v / 0.5}
    return {noms[1]: 1 - (v - 0.5) / 0.5, noms[2]: (v - 0.5) / 0.5}


def poids_age(annees: float) -> dict:
    """Âge réel -> poids baby/child/young/old (convention MakeHuman)."""
    reperes = [(1, "baby"), (11, "child"), (25, "young"), (90, "old")]
    for (a0, n0), (a1, n1) in zip(reperes, reperes[1:]):
        if annees <= a1:
            t = (annees - a0) / (a1 - a0)
            return {n0: 1 - t, n1: t}
    return {"old": 1.0}


def appliquer_macros(base, dossier: Path, age, muscle, poids, genre="male"):
    mac = dossier / "targets" / "macrodetails"
    w_age = poids_age(age)
    w_mus = {k + "muscle": w for k, w in poids_trois(muscle).items()}
    w_poi = {k + "weight": w for k, w in poids_trois(poids).items()}
    out = base.copy()
    for a, wa in w_age.items():
        # Cible d'ascendance : utilisée avec le poids MakeHuman standard.
        # Ce n'est pas une origine nationale ; la morphologie reste à valider.
        out += wa * lire_cible(mac / f"african-{genre}-{a}.target.gz", len(base))
        for m_, wm in w_mus.items():
            for p_, wp in w_poi.items():
                w = wa * wm * wp
                if w > 1e-4:
                    out += w * lire_cible(mac / f"universal-{genre}-{a}-{m_}-{p_}.target.gz", len(base))
    return out


def appliquer(base, dossier: Path, reglages: dict):
    out = base.copy()
    for rel, w in reglages.items():
        out += w * lire_cible(dossier / "targets" / f"{rel}.target.gz", len(base))
    return out


# --------------------------------------------------------------------------
# Personnages : une seule base de visage, deux âges
# --------------------------------------------------------------------------
VISAGE_COMMUN = {
    # Stylisation légère, identique aux deux âges (identité commune).
    "eyes/l-eye-scale-incr": .55, "eyes/r-eye-scale-incr": .55,
    "eyes/l-eye-height2-incr": .25, "eyes/r-eye-height2-incr": .25,
    "head/head-round": .35,
    "nose/nose-flaring-incr": .25, "nose/nose-point-width-incr": .2,
    "mouth/mouth-lowerlip-volume-incr": .25, "mouth/mouth-upperlip-volume-incr": .2,
    "mouth/mouth-scale-horiz-incr": .15,
    "chin/chin-prominent-decr": .2,
    "ears/l-ear-scale-decr": .15, "ears/r-ear-scale-decr": .15,
}
PERSONNAGES = {
    "adulte": dict(age=42, muscle=.45, poids=.68, specifique={
        "head/head-fat-incr": .45, "chin/chin-width-incr": .3, "neck/neck-double-incr": .15,
        "expression/units/african/mouth-corner-puller": .35,   # sourire discret
        "expression/units/african/eyebrows-left-inner-up": .35,  # nostalgie
        "expression/units/african/eyebrows-right-inner-up": .35,
        "expression/units/african/eye-left-slit": .12, "expression/units/african/eye-right-slit": .12,
    }, barbe=True, cheveux_longueur=.013, ligne_front=.062),
    # Âge corporel 18 : à 16 ans réels, la courbe MakeHuman donne un gabarit d'enfant (1,55 m).
    "ado": dict(age=18, muscle=.6, poids=.4, specifique={
        "head/head-age-decr": .5,
        "head/head-fat-decr": .25, "chin/chin-width-decr": .15,
        "expression/units/african/mouth-corner-puller": .6,     # sourire spontané
        "expression/units/african/eyebrows-left-up": .2, "expression/units/african/eyebrows-right-up": .2,
    }, barbe=False, cheveux_longueur=.02, ligne_front=.055),
}


# --------------------------------------------------------------------------
# Construction Blender
# --------------------------------------------------------------------------
def vers_blender(v: np.ndarray) -> np.ndarray:
    """Repère MakeHuman (Y haut, Z avant) -> Blender (Z haut, -Y avant), en mètres."""
    return np.stack([v[:, 0], -v[:, 2], v[:, 1]], axis=1) * ECHELLE


def objet_depuis_groupes(nom, verts_bl, uvs, groupes, noms_groupes, col):
    faces, faces_uv = [], []
    for g in noms_groupes:
        for f in groupes[g]:
            faces.append([p[0] for p in f])
            faces_uv.append([p[1] for p in f])
    utilises = sorted({i for f in faces for i in f})
    remap = {old: new for new, old in enumerate(utilises)}
    me = bpy.data.meshes.new(nom)
    me.from_pydata([tuple(verts_bl[i]) for i in utilises], [], [[remap[i] for i in f] for f in faces])
    uv = me.uv_layers.new(name="UVMap")
    k = 0
    for poly, fu in zip(me.polygons, faces_uv):
        for li, ui in zip(poly.loop_indices, fu):
            uv.data[li].uv = uvs[ui]
        k += 1
    me.shade_smooth() if hasattr(me, "shade_smooth") else None
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(nom, me)
    col.objects.link(ob)
    return ob, np.array(utilises)


def mat_peau(nom, dossier_tex: Path):
    mat = bpy.data.materials.new(nom)
    mat.use_nodes = True
    nt = mat.node_tree
    n = nt.nodes
    b = n["Principled BSDF"]
    # Peau foncée chaude ; nuances naturelles par bruit basse fréquence.
    bruit = n.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = 18.0
    bruit.inputs["Detail"].default_value = 3.0
    rampe = n.new("ShaderNodeValToRGB")
    rampe.color_ramp.elements[0].color = rc.hex_lineaire("#4B2F22")
    rampe.color_ramp.elements[1].color = rc.hex_lineaire("#674132")
    nt.links.new(bruit.outputs["Fac"], rampe.inputs["Fac"])
    # Lèvres : masque UV MakeHuman, teinte légèrement plus sombre et rosée.
    tex_l = n.new("ShaderNodeTexImage")
    tex_l.image = bpy.data.images.load(str(dossier_tex / "mpfb_lips.jpg"))
    tex_l.image.colorspace_settings.name = "Non-Color"
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(tex_l.outputs["Color"], mix.inputs["Factor"])
    nt.links.new(rampe.outputs["Color"], mix.inputs[6])
    mix.inputs[7].default_value = rc.hex_lineaire("#3A1F1C")
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.58
    b.inputs["Subsurface Weight"].default_value = 1.0
    b.inputs["Subsurface Radius"].default_value = (0.8, 0.45, 0.3)
    b.inputs["Subsurface Scale"].default_value = 0.004
    b.inputs["Specular IOR Level"].default_value = 0.32
    b.inputs["Coat Weight"].default_value = 0.0
    b.inputs["Coat Roughness"].default_value = 0.35
    # Micro-relief (pores) très léger
    bruit2 = n.new("ShaderNodeTexNoise")
    bruit2.inputs["Scale"].default_value = 900.0
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.06
    bump.inputs["Distance"].default_value = 0.0004
    nt.links.new(bruit2.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return mat


def mat_oeil(nom, oeil_obj, rayon):
    """Œil procédural : sclérotique, iris brun chaud avec stries, pupille, cornée vernie."""
    mat = bpy.data.materials.new(nom)
    mat.use_nodes = True
    nt = mat.node_tree
    n = nt.nodes
    b = n["Principled BSDF"]
    coord = n.new("ShaderNodeTexCoord")
    coord.object = oeil_obj
    sep = n.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
    # Distance radiale autour de l'axe de regard (-Y local), normalisée par le rayon.
    mx = n.new("ShaderNodeMath"); mx.operation = "MULTIPLY"
    nt.links.new(sep.outputs["X"], mx.inputs[0]); nt.links.new(sep.outputs["X"], mx.inputs[1])
    mz = n.new("ShaderNodeMath"); mz.operation = "MULTIPLY"
    nt.links.new(sep.outputs["Z"], mz.inputs[0]); nt.links.new(sep.outputs["Z"], mz.inputs[1])
    add = n.new("ShaderNodeMath"); add.operation = "ADD"
    nt.links.new(mx.outputs[0], add.inputs[0]); nt.links.new(mz.outputs[0], add.inputs[1])
    rac = n.new("ShaderNodeMath"); rac.operation = "SQRT"
    nt.links.new(add.outputs[0], rac.inputs[0])
    norm = n.new("ShaderNodeMath"); norm.operation = "DIVIDE"
    nt.links.new(rac.outputs[0], norm.inputs[0]); norm.inputs[1].default_value = rayon
    # Arrière de l'œil : forcer la sclérotique
    arriere = n.new("ShaderNodeMath"); arriere.operation = "GREATER_THAN"
    nt.links.new(sep.outputs["Y"], arriere.inputs[0]); arriere.inputs[1].default_value = 0.0
    maxi = n.new("ShaderNodeMath"); maxi.operation = "MAXIMUM"
    nt.links.new(norm.outputs[0], maxi.inputs[0]); nt.links.new(arriere.outputs[0], maxi.inputs[1])
    # Stries de l'iris : bruit étiré radialement
    stries = n.new("ShaderNodeTexNoise")
    stries.inputs["Scale"].default_value = 60.0
    stries.inputs["Detail"].default_value = 6.0
    nt.links.new(coord.outputs["Object"], stries.inputs["Vector"])
    rampe = n.new("ShaderNodeValToRGB")
    cr = rampe.color_ramp
    cr.interpolation = "LINEAR"
    cr.elements[0].position = 0.0
    cr.elements[0].color = rc.hex_lineaire("#050403")
    cr.elements[1].position = 0.17
    cr.elements[1].color = rc.hex_lineaire("#070504")
    for pos, coul in [(0.19, "#3B1F10"), (0.33, "#6A3A18"), (0.44, "#2A160C"),
                      (0.48, "#1A0F0A"), (0.53, "#D8CFC4"), (1.0, "#E6DDD2")]:
        e = cr.elements.new(pos)
        e.color = rc.hex_lineaire(coul)
    nt.links.new(maxi.outputs[0], rampe.inputs["Fac"])
    # Modulation de l'iris par les stries
    mixs = n.new("ShaderNodeMix"); mixs.data_type = "RGBA"; mixs.blend_type = "MULTIPLY"
    mixs.inputs["Factor"].default_value = 0.35
    nt.links.new(rampe.outputs["Color"], mixs.inputs[6])
    nt.links.new(stries.outputs["Color"], mixs.inputs[7])
    nt.links.new(mixs.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.25
    b.inputs["Subsurface Weight"].default_value = 0.3
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.02
    b.inputs["Coat IOR"].default_value = 1.376
    return mat


def mat_cheveux(nom, melanine=1.0):
    mat = bpy.data.materials.new(nom)
    mat.use_nodes = True
    nt = mat.node_tree
    for nd in list(nt.nodes):
        if nd.type == "BSDF_PRINCIPLED":
            nt.nodes.remove(nd)
    h = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    h.parametrization = "MELANIN"
    h.inputs["Melanin"].default_value = 0.92
    h.inputs["Melanin Redness"].default_value = 0.35
    h.inputs["Roughness"].default_value = 0.6
    h.inputs["Radial Roughness"].default_value = 0.6
    h.inputs["Random Roughness"].default_value = 0.3
    nt.links.new(h.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return mat


def systeme_poils(ob, nom, mat, nombre, longueur, enfants, boucle, groupe=None, rayon=0.00035,
                  ampl=0.0025, freq=45.0):
    mod = ob.modifiers.new(nom, "PARTICLE_SYSTEM")
    ps = mod.particle_system
    s = ps.settings
    s.name = nom
    s.type = "HAIR"
    s.count = nombre
    s.hair_length = longueur
    s.use_advanced_hair = False  # sinon la longueur suit normal_factor (1 = 1 m)
    s.child_type = "INTERPOLATED"
    s.child_percent = 3
    s.rendered_child_count = enfants
    s.child_length = 1.0
    s.clump_factor = 0.0
    s.roughness_1 = longueur * 0.35
    s.roughness_1_size = 0.05
    s.roughness_2 = longueur * 0.2
    s.roughness_endpoint = longueur * 0.1
    if boucle:
        s.kink = "CURL"
        s.kink_amplitude = ampl
        s.kink_frequency = freq
        s.kink_shape = 0.2
    s.radius_scale = rayon
    s.root_radius = 1.0
    s.tip_radius = 0.4
    ob.data.materials.append(mat)
    s.material = len(ob.data.materials)
    if groupe:
        ps.vertex_group_density = groupe
    return ps


def construire(nom, cfg, base, uvs, groupes, dossier, col, x_offset, m):
    v = appliquer_macros(base, dossier, cfg["age"], cfg["muscle"], cfg["poids"])
    v = appliquer(v, dossier, {**VISAGE_COMMUN, **cfg["specifique"]})
    vb = vers_blender(v)

    corps, idx_corps = objet_depuis_groupes(f"CHR_amadou{nom.capitalize()}_TETE_test", vb, uvs, groupes,
                                            ["body"], col)
    corps.data.materials.append(m["peau"])
    corps.location.x = x_offset
    sub = corps.modifiers.new("subdiv", "SUBSURF")
    sub.levels, sub.render_levels = 1, 2

    # Yeux : centre et rayon tirés de l'aide 'helper-?-eye' déformée par les cibles.
    for cote in ("l", "r"):
        ids = sorted({p[0] for f in groupes[f"helper-{cote}-eye"] for p in f})
        pts = vb[ids]
        centre = pts.mean(axis=0)
        r = float(np.linalg.norm(pts - centre, axis=1).mean())
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=r,
                                             location=Vector(centre) + Vector((x_offset, 0, 0)))
        oeil = bpy.context.object
        oeil.name = f"{corps.name}_oeil_{cote}"
        bpy.ops.object.shade_smooth()
        rc.lier(oeil, col)
        oeil.data.materials.append(mat_oeil(f"MAT_oeil_{nom}_{cote}", oeil, r))

    # Repères du visage (après déformation par les cibles)
    me = corps.data
    co = np.array([vv.co[:] for vv in me.vertices])
    oeil_l = vb[sorted({p[0] for f in groupes["helper-l-eye"] for p in f})].mean(axis=0)
    oeil_r = vb[sorted({p[0] for f in groupes["helper-r-eye"] for p in f})].mean(axis=0)
    ez = (oeil_l[2] + oeil_r[2]) / 2
    ex = abs(oeil_l[0] - oeil_r[0]) / 2
    face_y = co[:, 1][np.abs(co[:, 2] - ez) < 0.01].min()   # avant du visage (y le plus petit)
    devant = co[:, 1] < face_y + 0.055

    # Masques UV MakeHuman échantillonnés par sommet (visage, oreilles, lèvres)
    uvl = me.uv_layers["UVMap"].data
    uv_v = np.zeros((len(me.vertices), 2))
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uv_v[vi] = uvl[li].uv

    def masque(nom_tex):
        img = bpy.data.images.load(str(dossier / "textures" / f"{nom_tex}.jpg"), check_existing=True)
        w, h = img.size
        px = np.array(img.pixels[:]).reshape(h, w, 4)[:, :, 0]
        xi = np.clip((uv_v[:, 0] * w).astype(int), 0, w - 1)
        yi = np.clip((uv_v[:, 1] * h).astype(int), 0, h - 1)
        return px[yi, xi]

    m_visage, m_oreilles, m_levres = masque("mpfb_face"), masque("mpfb_ears"), masque("mpfb_lips")

    # Cuir chevelu : tête hors visage et oreilles ; ligne frontale progressive, nuque dégagée.
    g_cheveux = corps.vertex_groups.new(name="cuir_chevelu")
    profondeur = co[:, 1] - face_y                     # 0 = avant du visage
    for i, (x, y, z) in enumerate(co):
        lz = z - ez
        if lz < -0.10 or m_oreilles[i] > 0.2 or abs(x) > 0.11:
            continue
        if profondeur[i] < 0.075:                      # partie avant : front
            w_ = np.clip((lz - cfg["ligne_front"]) / 0.012, 0, 1)
        elif profondeur[i] < 0.13:                     # tempes / au-dessus des oreilles
            w_ = np.clip((lz - 0.012) / 0.015, 0, 1)
        else:                                          # arrière du crâne jusqu'à la nuque
            w_ = np.clip((lz + 0.075) / 0.02, 0, 1)
        w_ *= 1.0 - np.clip(m_visage[i] * 1.5, 0, 1) * (lz < cfg["ligne_front"] + 0.01)
        if w_ > 0.02:
            g_cheveux.add([i], float(w_), "REPLACE")
    systeme_poils(corps, f"PS_cheveux_{nom}", m["cheveux"], 30000, cfg["cheveux_longueur"], 40, True,
                  "cuir_chevelu", rayon=0.00028, ampl=0.003, freq=22)

    g_sourcils = corps.vertex_groups.new(name="sourcils")
    for i, (x, y, z) in enumerate(co):
        for cx in (-ex, ex):
            dx = (x - math.copysign(abs(cx) + 0.004, cx)) / 0.021
            dz = (z - (ez + 0.019 + 0.004 * (1 - min(1, abs(dx))) - 0.002 * dx * math.copysign(1, cx))) / 0.0034
            if dx * dx + dz * dz < 1 and devant[i]:
                g_sourcils.add([i], 1.0, "REPLACE")
    systeme_poils(corps, f"PS_sourcils_{nom}", m["cheveux"], 420, 0.005, 5, False, "sourcils", rayon=0.0002)

    if cfg["barbe"]:
        g_barbe = corps.vertex_groups.new(name="barbe")
        for i, (x, y, z) in enumerate(co):
            lz = z - ez
            if not (-0.135 < lz < -0.045) or abs(x) > 0.075 or profondeur[i] > 0.075:
                continue
            if m_levres[i] > 0.2:
                continue
            moustache = -0.075 < lz < -0.056 and abs(x) < 0.03
            menton = lz < -0.092 and abs(x) < 0.062
            if moustache or menton:
                g_barbe.add([i], 1.0, "REPLACE")
        systeme_poils(corps, f"PS_barbe_{nom}", m["cheveux"], 3500, 0.003, 20, True, "barbe",
                      rayon=0.00022, ampl=0.0008, freq=50)

    # Haut de vêtement simple (épaules) : copie gonflée du buste
    bpy.ops.object.select_all(action="DESELECT")
    return corps, ez, face_y


def vetement(corps, nom, mat, ez, col, x_offset):
    me = corps.data
    # Encolure ronde : plus basse devant, plus haute derrière
    sel = [v.index for v in me.vertices if v.co.z < ez - 0.145 - 0.03 * (v.co.y < 0)]
    ob = corps.copy()
    ob.data = me.copy()
    ob.name = f"{corps.name}_haut"
    for mod in list(ob.modifiers):
        ob.modifiers.remove(mod)
    col.objects.link(ob)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    keep = set(sel)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in keep], context="VERTS")
    for v in bm.verts:
        v.co += v.normal * 0.01
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    s = ob.modifiers.new("subdiv", "SUBSURF")
    s.levels, s.render_levels = 1, 2
    ob.modifiers.new("epaisseur", "SOLIDIFY").thickness = 0.004
    return ob


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--mpfb", required=True, help="Dossier data de MPFB (contient 3dobjs/ et targets/)")
    p.add_argument("--res", type=int, default=50)
    p.add_argument("--samples", type=int, default=96)
    p.add_argument("--version", type=int, default=1)
    a = p.parse_args(argv)
    dossier = Path(a.mpfb)
    if not dossier.is_absolute():
        dossier = rc.RACINE / dossier

    scene = rc.scene_vide()
    rc.reglages_rendu_test(scene, a.res, a.samples)
    scene.cycles.use_adaptive_sampling = True
    scene.view_settings.look = "AgX - Medium High Contrast"

    base, uvs, groupes = lire_obj(dossier / "3dobjs" / "base.obj")
    m = {
        "peau": mat_peau("MAT_peau_amadou_test", dossier / "textures"),
        "cheveux": mat_cheveux("MAT_cheveux_amadou_test"),
        "cuir_chevelu": rc.materiau("MAT_cuir_chevelu", "#20140F", .8),
        "haut_adulte": rc.materiau("MAT_sweat_marine", rc.PALETTE["bleu_nuit"], .85),
        "maillot": rc.materiau("MAT_maillot_bordeaux", rc.PALETTE["bordeaux"], .6),
    }
    col = rc.collection("TEST_tetes")
    ecart = 0.42
    resultats = {}
    for nom, x in (("adulte", -ecart / 2), ("ado", ecart / 2)):
        corps, ez, face_y = construire(nom, PERSONNAGES[nom], base, uvs, groupes, dossier, col, x, m)
        vetement(corps, nom, m["haut_adulte" if nom == "adulte" else "maillot"], ez, col, x)
        resultats[nom] = (corps, ez, face_y)

    # Fond chaud et flou (fin de journée), commun aux deux portraits
    world = bpy.data.worlds.new("WLD_portrait")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = rc.hex_lineaire("#6E5E52")
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 1.2, 0.9))
    fond = bpy.context.object
    fond.scale = (6, 4, 1)
    fond.rotation_euler.x = math.radians(90)
    fond.data.materials.append(rc.materiau("MAT_fond_portrait", "#8C7462", .9))
    rc.lier(fond, col)

    cd = bpy.data.cameras.new("CAM_portrait")
    cd.lens = 85
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 2.8
    cam = bpy.data.objects.new("CAM_portrait", cd)
    col.objects.link(cam)
    scene.camera = cam
    lumieres = []
    for nom_l, e, c, taille in [("cle", 60, "#FFE7CF", 1.0), ("contre", 45, "#FFD9B0", .6),
                                ("debouchage", 22, "#D5DFF0", 1.4)]:
        ld = bpy.data.lights.new(f"LGT_{nom_l}", "AREA")
        ld.energy, ld.size = e, taille
        ld.color = rc.hex_lineaire(c)[:3]
        lo = bpy.data.objects.new(f"LGT_{nom_l}", ld)
        col.objects.link(lo)
        lumieres.append(lo)

    # Portrait vertical 4:5 par personnage, puis assemblage côte à côte (format 16:9 conservé)
    scene.render.resolution_x = 864
    scene.render.resolution_y = 1080
    v = f"v{a.version:03d}"
    images, duree = [], 0.0
    for nom, (corps, ez, face_y) in resultats.items():
        for o in col.objects:
            if o.name.startswith("CHR_"):
                o.hide_render = not o.name.startswith(corps.name)
        cx = corps.location.x
        tete = Vector((cx, face_y + 0.09, ez - 0.03))
        cam.location = (cx + 0.18, face_y - 1.15, ez - 0.01)
        cam.rotation_euler = (tete - cam.location).to_track_quat("-Z", "Y").to_euler()
        cd.dof.focus_distance = (Vector((cx - 0.01, face_y, ez)) - cam.location).length
        for lo, off in zip(lumieres, [(-0.75, -0.75, 0.45), (0.55, 0.65, 0.35), (0.9, -0.9, -0.05)]):
            lo.location = tete + Vector(off)
            lo.rotation_euler = (tete - lo.location).to_track_quat("-Z", "Y").to_euler()
        chemin = rc.RENDUS_TESTS / "CHR_amadou" / f"CHR_amadou{nom.capitalize()}_TETE_test_{v}.png"
        duree += rc.rendre(scene, chemin)
        images.append(chemin)

    # Planche : adulte | ado
    pix = []
    for ch in images:
        im = bpy.data.images.load(str(ch))
        w, h = im.size
        pix.append(np.array(im.pixels[:]).reshape(h, w, 4))
    planche = np.concatenate(pix, axis=1)
    h, w = planche.shape[:2]
    out = bpy.data.images.new("planche", w, h, alpha=True)
    out.pixels = planche.ravel()
    out.filepath_raw = str(rc.RENDUS_TESTS / "CHR_amadou" / f"CHR_amadou_TETE_test_{v}_planche.png")
    out.file_format = "PNG"
    out.save()
    print("[BILAN] rendu total", round(duree, 1), "s")
    for o in col.objects:
        o.hide_render = False
    rc.sauver_blend(rc.ASSETS / "personnages" / "CHR_amadou" / f"CHR_amadou_TETE_test_{v}.blend")


if __name__ == "__main__":
    main()
