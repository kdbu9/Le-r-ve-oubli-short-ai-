"""Produit des prompts complets, prêts à copier-coller, pour chaque plan.

Remplace les codes [STYLE] / [LUM_…] / [DECOR_…] / [PERSO_…] du découpage par
les blocs de texte de 08_PIPELINE_VIDEO_IA/BIBLE_PROMPTS.md (source unique).
Lancement depuis la racine du dépôt :
    python scripts/ia/assembler_prompts.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DOSSIER = RACINE / "08_PIPELINE_VIDEO_IA"


def lire_blocs() -> dict[str, str]:
    texte = (DOSSIER / "BIBLE_PROMPTS.md").read_text(encoding="utf-8")
    blocs = {}
    # Blocs de code précédés d'une ligne contenant `CODE` ou « Bloc STYLE »
    for m in re.finditer(r"(?P<entete>[^\n]*)\n(?:[^\n`]*\n)?```\n(?P<corps>.*?)\n```", texte, re.S):
        codes = re.findall(r"`([A-Z]+_[A-Z_]+)`", m.group("entete"))
        if "Bloc STYLE" in m.group("entete"):
            codes = ["STYLE"]
        for c in codes:
            blocs.setdefault(c, m.group("corps").strip())
    for code, bloc in re.findall(r"\| `(LUM_[A-Z]+)` \|[^|]*\| `([^`]*)` \|", texte):
        blocs[code] = bloc
    # Bloc STYLE : premier bloc de code de la section 2
    sec = texte.split("## 2.")[1]
    blocs["STYLE"] = re.search(r"```\n(.*?)\n```", sec, re.S).group(1).strip()
    return blocs


def main() -> None:
    blocs = lire_blocs()
    with open(DOSSIER / "DECOUPAGE_PLANS_IA.csv", encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    md = ["# Prompts complets — prêts à copier-coller", "",
          "> Généré par `scripts/ia/assembler_prompts.py` à partir de `BIBLE_PROMPTS.md` et `DECOUPAGE_PLANS_IA.csv`.",
          "> Pour chaque plan : 1) générer l'IMAGE avec Nano Banana Pro, format 16:9, en joignant les références indiquées ;",
          "> 2) passer l'image retenue dans Seedance avec le prompt VIDÉO et la durée indiquée.", ""]
    manquants = set()
    for l in lignes:
        if l["type"] == "montage":
            md += [f"## {l['plan']} — {l['debut']}–{l['fin']} — MONTAGE (rien à générer)",
                   f"{l['prompt_video']}", ""]
            continue

        def remplacer(m):
            c = m.group(1)
            if c not in blocs:
                manquants.add(c)
                return m.group(0)
            return blocs[c]

        action = re.sub(r"\[([A-Z]+_[A-Z_]+)\]", remplacer, l["prompt_image_cle"])
        image = " ".join([blocs["STYLE"], blocs.get(l["lumiere"], ""), action, "16:9 widescreen frame."])
        image = re.sub(r"\s+", " ", image).strip()
        refs = ", ".join(f"`{r.strip()}.png`" for r in l["references"].split("+")) if l["references"] != "-" else "aucune"
        md += [f"## {l['plan']} — {l['debut']}–{l['fin']} — {l['duree_s']} s",
               f"**Références à joindre :** {refs}", "",
               "**IMAGE (Nano Banana Pro, 16:9)**", "```", image, "```",
               f"**VIDÉO (Seedance, {l['duree_s']} s, 16:9)**", "```",
               f"{l['prompt_video']} Keep the same character design, face and stylized 3D animated look as the start image. No text.",
               "```", f"*Son / dialogue (ajouté au montage) : {l['son_dialogue']}*", ""]
    if manquants:
        raise SystemExit(f"Codes sans bloc dans la bible : {sorted(manquants)}")
    (DOSSIER / "PROMPTS_COMPLETS.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(lignes)} plans → 08_PIPELINE_VIDEO_IA/PROMPTS_COMPLETS.md")


if __name__ == "__main__":
    main()
