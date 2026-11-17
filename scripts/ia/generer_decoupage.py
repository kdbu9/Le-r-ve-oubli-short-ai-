"""Génère le découpage plan par plan du pipeline vidéo IA (CSV + Markdown).

Source unique de vérité : la liste PLANS ci-dessous. Elle respecte le minutage
de 04_SCENARIO_STORYBOARD/LISTE_PLANS_PROVISOIRE.csv (180 s) et le scénario
verrouillé. Lancement depuis la racine du dépôt :
    python scripts/ia/generer_decoupage.py
"""
from __future__ import annotations

import csv
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "08_PIPELINE_VIDEO_IA"

RA = "REF_amadouAdulte_visage + REF_amadouAdulte_turnaround"
RT = "REF_amadouAdo_visage + REF_amadouAdo_turnaround"
RM = "REF_mere_portrait + REF_mere_turnaround + REF_mere_expressions"

# (plan, durée s, lumière, références, image clé, mouvement vidéo, dialogue/son, note)
PLANS = [
    # --- SQ010 Présent (0:00–0:30) ---
    ("SQ010_SH010_C01", 8, "LUM_PRESENT", "-", "[DECOR_QUARTIER] Wide establishing shot of the neighborhood in the morning, buildings, trees, a few passers-by, the football pitch visible in the distance.",
     "Slow lateral camera glide across the neighborhood, gentle life: a bus passes, pigeons take off, distant kids' voices.", "Ambiance quartier, circulation, enfants au loin", ""),
    ("SQ010_SH020_C01", 5, "LUM_PRESENT", RA, "[DECOR_QUARTIER] [PERSO_AMADOU_ADULTE] Medium-wide shot, Amadou sweeping the sidewalk with his long street broom, his green wheeled street-cleaning cart with a bin beside him, a few dry leaves and papers on the ground.",
     "Amadou sweeps calmly and methodically in long regular strokes, pushing leaves and papers into a small pile, static camera.", "Balai sur le bitume, feuilles, roulettes du chariot", "Agent de propreté qui balaie les rues (validé)"),
    ("SQ010_SH020_C02", 5, "LUM_PRESENT", RA, "[PERSO_AMADOU_ADULTE] Medium shot from the side, Amadou leaning on his broom handle, slightly tired expression, his cleaning cart behind him.",
     "He pauses, wipes his forehead with the back of his hand, then starts sweeping again. Subtle handheld feel.", "Souffle, balai, pelle", ""),
    ("SQ010_SH030_C01", 4, "LUM_PRESENT", "-", "[DECOR_TERRAIN] [PERSO_ENFANTS_PRESENT] Wide shot of kids playing football on the neighborhood pitch.",
     "Kids run after the ball, one dribbles past another, joyful energy, camera follows the ball.", "Rebonds, cris joyeux", ""),
    ("SQ010_SH030_C02", 4, "LUM_PRESENT", RA, "[PERSO_AMADOU_ADULTE] Medium close-up, Amadou holding his broom, lifts his head toward the sound of the ball, the pitch blurred in the background.",
     "His broom slows down and stops; he turns his head toward the kids, his eyes follow the ball.", "Bruit de ballon plus présent", "Raccord regard"),
    ("SQ010_SH030_C03", 4, "LUM_PRESENT", RA, "[PERSO_AMADOU_ADULTE] Close-up on Amadou's face looking off-screen, soft nostalgic expression.",
     "Very slow push-in on his eyes, a faint smile appears, the sound around him fades.", "Début du thème musical, très discret", "Entrée dans la rêverie"),
    # --- SQ020 Souvenir (0:30–1:15) ---
    ("SQ020_SH010_C01", 5, "LUM_SOUVENIR", "-", "[DECOR_TERRAIN] Close-up of a football bouncing on the pitch, golden light flaring.",
     "The ball bounces in slow motion; the light warms up and becomes golden, as if the image is remembering.", "Transition sonore, thème qui monte", "Transition lumineuse présent → souvenir (fondu au montage)"),
    ("SQ020_SH010_C02", 5, "LUM_SOUVENIR", RT, "[DECOR_TERRAIN] [PERSO_AMADOU_ADO] Medium shot, young Amadou catches the ball with his foot and looks up, beaming.",
     "He controls the ball with ease and smiles; camera slowly rises to reveal the match.", "Thème ample", ""),
    ("SQ020_SH020_C01", 5, "LUM_SOUVENIR", RT, "[DECOR_TERRAIN] [PERSO_AMADOU_ADO] [PERSO_EQUIPES_SOUVENIR] Wide shot, Amadou running with the ball toward two defenders.",
     "Amadou dribbles past the first defender with a quick body feint, clear and readable action, camera tracks sideways.", "Frappes, pas, percussions", "Dribble lisible : géographie cohérente"),
    ("SQ020_SH020_C02", 5, "LUM_SOUVENIR", RT, "[PERSO_AMADOU_ADO] [PERSO_EQUIPES_SOUVENIR] Low-angle tracking shot following Amadou's feet and the ball.",
     "Fast close footwork, he passes the ball between a defender's legs and recovers it.", "Rythme musical synchronisé", ""),
    ("SQ020_SH020_C03", 4, "LUM_SOUVENIR", "-", "[PERSO_EQUIPES_SOUVENIR] Medium shot of two surprised defenders turning around.",
     "The defenders spin around, stunned, one laughs in disbelief.", "Réactions", ""),
    ("SQ020_SH020_C04", 5, "LUM_SOUVENIR", "-", "[DECOR_TERRAIN] Parents and neighbors watching from the fence, amazed.",
     "They lean forward, someone points, a mother claps, admiration on their faces.", "Applaudissements", "Les parents spectateurs, pas la mère d'Amadou"),
    ("SQ020_SH020_C05", 6, "LUM_SOUVENIR", RT, "[DECOR_TERRAIN] [PERSO_AMADOU_ADO] Wide shot, Amadou in front of the goal.",
     "He shoots, the ball hits the back of the net, he raises his arms in joy.", "Frappe, filet, explosion musicale", ""),
    ("SQ020_SH030_C01", 5, "LUM_SOUVENIR", RT, "[PERSO_AMADOU_ADO] [PERSO_EQUIPES_SOUVENIR] Teammates in burgundy rushing to hug Amadou.",
     "They jump on him, laughing, ruffling his hair, a joyful pile of teenagers.", "Rires, cris de joie", ""),
    ("SQ020_SH030_C02", 5, "LUM_SOUVENIR", RT, "[PERSO_ENTRAINEUR] [PERSO_AMADOU_ADO] Medium shot, the coach puts a proud hand on Amadou's shoulder.",
     "The coach nods with pride; close on Amadou, radiant, full of hope.", "Thème à son sommet", "Il semble avoir un avenir dans le football"),
    # --- SQ030 Conflit familial (1:15–1:55) ---
    ("SQ030_SH010_C01", 4, "LUM_MAISON", "-", "[DECOR_QUARTIER] Exterior of the family's apartment building at dusk, a few lit windows.",
     "Slow push-in toward one warmly lit window.", "Ambiance du soir, musique réduite", "Transition vers le foyer"),
    ("SQ030_SH010_C02", 6, "LUM_MAISON", RT + " + " + RM, "[DECOR_SALON] [PERSO_AMADOU_ADO] [PERSO_MERE] Amadou comes in, ball under his arm, still glowing; his mother sits at the table with his school notebooks open.",
     "He enters smiling; she looks up from the notebooks, gentle but serious.", "Porte, pas, silence", "Décor : salon (validé)"),
    ("SQ030_SH020_C01", 5, "LUM_MAISON", RM, "[PERSO_MERE] Medium close-up of the mother, a notebook in her hand.",
     "She speaks calmly, tapping the notebook softly, caring but firm.", "DIA_MERE_01 (lipsync)", "Dialogue à valider"),
    ("SQ030_SH020_C02", 5, "LUM_MAISON", RT, "[PERSO_AMADOU_ADO] Medium close-up of Amadou, holding the ball.",
     "He answers with passion, eyes shining, gesturing toward the window and the pitch.", "DIA_AMADOU_01 (lipsync)", ""),
    ("SQ030_SH020_C03", 5, "LUM_MAISON", RM, "[PERSO_MERE] Close-up of the mother, worried and loving.",
     "She shakes her head slowly, her eyes full of worry for his future.", "DIA_MERE_02 (lipsync)", "Jamais cruelle"),
    ("SQ030_SH020_C04", 5, "LUM_MAISON", RT, "[PERSO_AMADOU_ADO] Close-up of Amadou, his smile fading.",
     "His face falls, he looks down at the ball in his hands.", "Silence, piano", ""),
    ("SQ030_SH020_C05", 5, "LUM_MAISON", RT + " + " + RM, "[PERSO_MERE] [PERSO_AMADOU_ADO] Two-shot, she places her hand tenderly on his shoulder.",
     "She squeezes his shoulder gently, a sad loving smile; he doesn't look at her.", "DIA_MERE_03 (option), piano", "Affection et fermeté coexistent"),
    ("SQ030_SH020_C06", 5, "LUM_MAISON", RT, "[DECOR_SALON] [PERSO_AMADOU_ADO] Wide shot, Amadou alone, the ball on the floor beside the table.",
     "He slowly sits down in front of the open notebooks.", "Chaise, pages", ""),
    # --- SQ040 Renoncement (1:55–2:25) ---
    ("SQ040_SH010_C01", 5, "LUM_RENONCEMENT", "-", "[DECOR_CHAMBRE] The football in a corner of the bedroom, open notebooks on the desk.",
     "Static shot; the light slowly shifts across the room.", "Thème ralenti", "Le ballon, élément visuel du renoncement"),
    ("SQ040_SH010_C02", 5, "LUM_RENONCEMENT", RT, "[DECOR_CHAMBRE] [PERSO_AMADOU_ADO] Amadou studying at his desk at night, desk lamp on.",
     "He writes, stops, glances at the ball in the corner, then goes back to his notebook.", "Crayon, pages", ""),
    ("SQ040_SH010_C03", 5, "LUM_RENONCEMENT", "-", "[DECOR_CHAMBRE] The same corner: the ball slowly loses its shine, dust, a pile of books grows beside it.",
     "Time-lapse feeling: light cycles day and night through the window, books pile up.", "Thème fragmenté", "Le temps passe"),
    ("SQ040_SH020_C01", 5, "LUM_RENONCEMENT", RT, "[PERSO_AMADOU_ADO] Close-up of hands putting the burgundy jersey away in a drawer.",
     "The hands fold the jersey and slowly close the drawer.", "Tiroir", ""),
    ("SQ040_SH020_C02", 5, "LUM_RENONCEMENT", RA, "[PERSO_AMADOU_ADULTE] Adult Amadou putting on his yellow high-visibility vest in a locker room.",
     "He zips up the vest, a neutral, resigned face.", "Fermeture éclair", "Transition visuelle vers l'adulte"),
    ("SQ040_SH020_C03", 5, "LUM_PRESENT", RA, "[DECOR_QUARTIER] [PERSO_AMADOU_ADULTE] Amadou pushing his street-cleaning cart down the morning street, broom in hand.",
     "He walks away from the camera pushing the cart, then starts sweeping the gutter, routine.", "Ambiance du matin, roulettes du chariot, balai", "Il exerce un métier qu'il n'avait pas choisi"),
    # --- SQ050 Retour au présent (2:25–3:00) ---
    ("SQ050_SH010_C01", 5, "LUM_PRESENT", "-", "[DECOR_TERRAIN] [PERSO_ENFANTS_PRESENT] The same pitch in the present, the kids still playing.",
     "Camera slowly pulls back from the pitch, matching the earlier memory framing.", "Retour discret du thème", "Raccord avec SQ020"),
    ("SQ050_SH010_C02", 5, "LUM_PRESENT", RA, "[PERSO_AMADOU_ADULTE] Medium shot, Amadou watching the kids, leaning on his broom, his cart beside him.",
     "He watches, motionless, a soft nostalgic smile.", "Thème", ""),
    ("SQ050_SH010_C03", 5, "LUM_PRESENT", "-", "[PERSO_ENFANTS_PRESENT] A kid dribbles past another with the same feint young Amadou used.",
     "The kid performs the feint, laughing.", "Rebond, rires", "Écho du souvenir, sans transmission explicite"),
    ("SQ050_SH020_C01", 5, "LUM_PRESENT", RA, "[PERSO_COLLEGUE] [PERSO_AMADOU_ADULTE] The co-worker a few meters away, calling out to Amadou.",
     "The co-worker calls him with a friendly wave.", "DIA_COLLEGUE : « Allez, au boulot, on a du travail ! » (lipsync, réplique exacte)", "Réplique verrouillée"),
    ("SQ050_SH020_C02", 5, "LUM_PRESENT", RA, "[PERSO_AMADOU_ADULTE] Close-up, Amadou snaps out of his daydream.",
     "He blinks, comes back to reality, a small nod.", "Thème interrompu", ""),
    ("SQ050_SH030_C01", 6, "LUM_PRESENT", RA, "[DECOR_TERRAIN] [PERSO_AMADOU_ADULTE] [PERSO_ENFANTS_PRESENT] Amadou in the foreground, kids playing in the background.",
     "He looks at the kids one last time, then lowers his eyes, starts sweeping again and moves away with his cart, leaving them to play. He says nothing.", "Laisser respirer ; le balai reprend", "Ne pas parler aux enfants, ne pas les encourager"),
    ("SQ050_SH040_C01", 4, "-", "-", "MONTAGE — écran noir, aucun visuel généré.",
     "Texte exact au montage : « N'éteignez pas leurs rêves. » puis « Un talent a besoin d'être encouragé, pas étouffé. »", "Silence ou dernière note", "Carton final verrouillé"),
]


def main() -> None:
    total = sum(p[1] for p in PLANS)
    assert total == 180, f"Durée totale {total} s au lieu de 180 s"
    lignes, t = [], 0
    for plan, duree, lum, refs, img, vid, son, note in PLANS:
        debut, t = t, t + duree
        tc = lambda s: f"{s // 60}:{s % 60:02d}"
        gen = "montage" if lum == "-" else "image clé → vidéo"
        lignes.append({"plan": plan, "debut": tc(debut), "fin": tc(t), "duree_s": duree, "type": gen,
                       "lumiere": lum, "references": refs, "prompt_image_cle": img,
                       "prompt_video": vid, "son_dialogue": son, "notes": note, "statut": "à générer"})
    with open(SORTIE / "DECOUPAGE_PLANS_IA.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    md = ["# Découpage plan par plan — génération vidéo IA", "",
          f"> Généré par `scripts/ia/generer_decoupage.py`. {len(lignes) - 1} générations + 1 carton de montage, durée totale {total} s.",
          "> Les codes entre crochets renvoient aux blocs de `BIBLE_PROMPTS.md`. Ajouter toujours le bloc STYLE et le code lumière.", ""]
    for l in lignes:
        md += [f"### {l['plan']} — {l['debut']}–{l['fin']} ({l['duree_s']} s) · {l['lumiere']}",
               f"- **Références :** {l['references']}",
               f"- **Image clé :** {l['prompt_image_cle']}",
               f"- **Vidéo :** {l['prompt_video']}",
               f"- **Son / dialogue :** {l['son_dialogue']}"]
        if l["notes"]:
            md.append(f"- **Note :** {l['notes']}")
        md.append("")
    (SORTIE / "DECOUPAGE_PLANS_IA.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(lignes)} plans, {total} s")


if __name__ == "__main__":
    main()
