"""Assemble l'animatique / le montage de travail du pipeline vidéo IA.

Pour chaque plan de 08_PIPELINE_VIDEO_IA/DECOUPAGE_PLANS_IA.csv :
- si un clip généré existe dans production/ia/clips/ (nom commençant par
  l'identifiant du plan, ex. SQ020_SH020_C01_v002.mp4 ; la version la plus
  récente est prise), il est recadré en 16:9, ramené à 24 i/s et coupé ou
  prolongé à la durée prévue ;
- sinon, une vignette provisoire affiche l'identifiant, le minutage et l'action.

Le carton final est TOUJOURS fabriqué ici, jamais généré par IA, avec les
textes exacts du scénario verrouillé.

Dépendance : FFmpeg compilé avec drawtext (libfreetype).
Lancement depuis la racine du dépôt :
    python scripts/ia/assembler_animatique.py --version 1
    python scripts/ia/assembler_animatique.py --largeur 1920 --audio   # garde le son des clips
"""
from __future__ import annotations

import argparse
import re
import csv
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DECOUPAGE = RACINE / "08_PIPELINE_VIDEO_IA" / "DECOUPAGE_PLANS_IA.csv"
CLIPS = RACINE / "production" / "ia" / "clips"
SORTIE = RACINE / "production" / "montage"
FPS = 24

# Textes verrouillés (SCENARIO_VERROUILLE.md) — ne pas modifier.
TEXTE_FINAL_1 = "N'éteignez pas leurs rêves."
TEXTE_FINAL_2 = "Un talent a besoin d'être encouragé, pas étouffé."

COULEURS = {  # fond des vignettes provisoires, d'après la bible graphique
    "LUM_PRESENT": "0x243B5A", "LUM_SOUVENIR": "0x9A6420", "LUM_MAISON": "0x6B3A2A",
    "LUM_RENONCEMENT": "0x3F4A4F", "-": "0x000000",
}
POLICES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def ffmpeg(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def echapper_chemin(p: Path) -> str:
    return str(p).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def clip_existant(plan: str) -> Path | None:
    if not CLIPS.exists():
        return None
    candidats = sorted(CLIPS.glob(f"{plan}*.mp4"))
    return candidats[-1] if candidats else None


def segment_clip(src: Path, duree: int, l: int, h: int, audio: bool, out: Path) -> None:
    vf = (f"scale={l}:{h}:force_original_aspect_ratio=increase,crop={l}:{h},fps={FPS},"
          f"tpad=stop_mode=clone:stop_duration={duree},trim=duration={duree},setpts=PTS-STARTPTS")
    args = ["-i", str(src)]
    if audio:
        args += ["-f", "lavfi", "-t", str(duree), "-i", "anullsrc=r=48000:cl=stereo",
                 "-filter_complex", f"[0:v]{vf}[v];[0:a][1:a]amix=inputs=2:duration=longest,"
                 f"atrim=duration={duree}[a]", "-map", "[v]", "-map", "[a]"]
    else:
        args += ["-f", "lavfi", "-t", str(duree), "-i", "anullsrc=r=48000:cl=stereo",
                 "-vf", vf, "-map", "0:v", "-map", "1:a"]
    ffmpeg(args + ["-t", str(duree), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                   "-ar", "48000", str(out)])


def segment_vignette(ligne: dict, l: int, h: int, police: Path, tmp: Path, out: Path) -> None:
    duree = int(ligne["duree_s"])
    titre = tmp / f"{ligne['plan']}_t.txt"
    corps = tmp / f"{ligne['plan']}_c.txt"
    titre.write_text(f"{ligne['plan']}   {ligne['debut']}–{ligne['fin']}   (vignette provisoire)",
                     encoding="utf-8")
    # Retire les codes de la bible (DECOR_, PERSO_, LUM_) ; garde les marqueurs à définir.
    action = re.sub(r"\[(DECOR|PERSO|LUM)_[A-Z_]+\]\s*", "", ligne["prompt_image_cle"]).strip()
    texte = textwrap.fill(action, 60) + "\n\n" + textwrap.fill("Son : " + ligne["son_dialogue"], 60)
    corps.write_text(texte, encoding="utf-8")
    fs = max(14, h // 28)
    vf = (f"drawtext=fontfile='{echapper_chemin(police)}':textfile='{echapper_chemin(titre)}':"
          f"fontcolor=white:fontsize={fs + 4}:x=(w-tw)/2:y=h*0.18,"
          f"drawtext=fontfile='{echapper_chemin(police)}':textfile='{echapper_chemin(corps)}':"
          f"fontcolor=white@0.9:fontsize={fs}:line_spacing={fs // 2}:x=(w-tw)/2:y=h*0.36")
    couleur = COULEURS.get(ligne["lumiere"], "0x222222")
    ffmpeg(["-f", "lavfi", "-i", f"color=c={couleur}:s={l}x{h}:r={FPS}:d={duree}",
            "-f", "lavfi", "-t", str(duree), "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", vf, "-t", str(duree), "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", str(out)])


def segment_carton_final(duree: int, l: int, h: int, police: Path, tmp: Path, out: Path) -> None:
    t1, t2 = tmp / "final_1.txt", tmp / "final_2.txt"
    t1.write_text(TEXTE_FINAL_1, encoding="utf-8")
    t2.write_text(TEXTE_FINAL_2, encoding="utf-8")
    fs = max(16, h // 18)
    p = echapper_chemin(police)
    # Ligne 1 apparaît en fondu à 0,4 s, ligne 2 à 1,8 s.
    a1 = "if(lt(t,0.4),0,if(lt(t,1.2),(t-0.4)/0.8,1))"
    a2 = "if(lt(t,1.8),0,if(lt(t,2.6),(t-1.8)/0.8,1))"
    vf = (f"drawtext=fontfile='{p}':textfile='{echapper_chemin(t1)}':fontcolor=white:fontsize={fs}:"
          f"x=(w-tw)/2:y=h*0.40:alpha='{a1}',"
          f"drawtext=fontfile='{p}':textfile='{echapper_chemin(t2)}':fontcolor=white:fontsize={int(fs * .75)}:"
          f"x=(w-tw)/2:y=h*0.53:alpha='{a2}'")
    ffmpeg(["-f", "lavfi", "-i", f"color=c=black:s={l}x{h}:r={FPS}:d={duree}",
            "-f", "lavfi", "-t", str(duree), "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", vf, "-t", str(duree), "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", str(out)])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", type=int, default=1)
    ap.add_argument("--largeur", type=int, default=1280, help="Largeur de sortie (16:9)")
    ap.add_argument("--audio", action="store_true", help="Conserver le son des clips générés")
    ap.add_argument("--police", type=Path, default=None, help="Fichier de police .ttf")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        raise SystemExit("FFmpeg introuvable.")
    police = a.police or next((Path(p) for p in POLICES if Path(p).exists()), None)
    if police is None:
        raise SystemExit("Aucune police trouvée : préciser --police chemin/vers/police.ttf")
    l = a.largeur - a.largeur % 2
    h = (l * 9 // 16) - (l * 9 // 16) % 2

    with open(DECOUPAGE, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    SORTIE.mkdir(parents=True, exist_ok=True)
    nb_clips = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        segments = []
        for i, ligne in enumerate(lignes):
            seg = tmp / f"{i:03d}_{ligne['plan']}.mp4"
            duree = int(ligne["duree_s"])
            if ligne["plan"].startswith("SQ050_SH040"):
                segment_carton_final(duree, l, h, police, tmp, seg)
            elif (src := clip_existant(ligne["plan"])) is not None:
                segment_clip(src, duree, l, h, a.audio, seg)
                nb_clips += 1
            else:
                segment_vignette(ligne, l, h, police, tmp, seg)
            segments.append(seg)
        liste = tmp / "liste.txt"
        liste.write_text("".join(f"file '{s.as_posix()}'\n" for s in segments), encoding="utf-8")
        sortie = SORTIE / f"ANIMATIQUE_IA_v{a.version:03d}.mp4"
        ffmpeg(["-f", "concat", "-safe", "0", "-i", str(liste), "-c", "copy", str(sortie)])
    duree_reelle = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(sortie)],
        capture_output=True, text=True).stdout.strip()
    print(f"{sortie.relative_to(RACINE)} — {len(lignes)} plans dont {nb_clips} clips générés, "
          f"durée {float(duree_reelle):.2f} s")


if __name__ == "__main__":
    main()
